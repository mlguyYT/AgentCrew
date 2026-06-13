"""Classifier-driven orchestrator.

the engine's job: execute the workflow that the classifier script has already
decided. No re-classification, no parallel intelligence layer.

Flow:
  1. classify(task)  →  Routing  (calls the classifier script)
  2. write current-task.md + task-routing.md per the state schema
  3. (optional) human gate on the routing (CLI shows it, asks yes/no)
  4. for each acting role in workflow:
        - build_agent(root, role, model)  (role file from agent-team)
        - provider.run_agent(...) with bounded tools per tools.build_tools(role)
        - parse the role's Handoff
        - persist per state-artifacts.md (handoff.md, role-report.md)
        - route: human-gate decision stops; rework decision routes back
  5. Stop when workflow finishes or a human-gate decision is reached.

The orchestrator is the only thing that mutates .agent-state/.
"""

from __future__ import annotations

import json
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import time as _time

from .agents import Agent, build_agent
from .config import ProjectConfig
from .decisions import load_recent as load_recent_decisions, render_section as render_decisions_section
from .telemetry import emit_run_event
from .cost import (
    CostGate,
    RunEstimate,
    actual_cost_from_usage,
    decide_cost_gate,
    estimate_run,
    load_daily_so_far,
    record_run_cost,
)
from .gates import load_gates_for_role, render_gate_section
from .handoff import (
    APPROVAL_DECISIONS,
    BLOCKING_DECISIONS,
    HUMAN_GATE_DECISIONS,
    REWORK_DECISIONS,
    Handoff,
    submit_handoff_input_schema,
)
from .provider import AgentRun, Provider
from .routing import Routing, classify
from .state import (
    StateLayout,
    build_layout,
    write_current_task,
    write_handoff,
    write_routing,
)
from .tools import build_tools
from .agentcrew_root import AgentCrewRoot


# Callback types.
# RoutingApprover: shown the Routing once before any role runs.
# RiskAcceptor: shown when the classifier inserts 'Human decision' mid-workflow.
# CostApprover: shown when the estimated run cost exceeds per_run_warn_usd
#   (warn) or per_run_block_usd / daily cap (block). Block returns False if
#   the user declines; warn returns True for approval. Auto-approver below
#   approves warnings, declines blocks.
RoutingApprover = Callable[[Routing], bool]
RiskAcceptor = Callable[[Routing, str], bool]  # (routing, role_about_to_run)
CostApprover = Callable[[CostGate], bool]      # returns True to proceed


def auto_approve(_r: Routing) -> bool:
    return True


def require_explicit_risk_acceptance(_r: Routing, _role: str) -> bool:
    """Safe default for human-only risk gates.

    Callers that have a real human confirmation surface should pass their own
    callback. The engine must not accept critical risk by default.
    """
    return False


def auto_approve_cost(gate: CostGate) -> bool:
    """Approve warnings; decline blocks. Safe default for scripted runs."""
    return not gate.block


@dataclass
class TeamRun:
    run_id: str
    task: str
    project_dir: Path
    run_dir: Path
    routing: Routing
    handoffs: list[Handoff] = field(default_factory=list)
    final_decision: str = ""
    next_owner: str = ""
    agent_runs: list[AgentRun] = field(default_factory=list)
    cost_estimate: RunEstimate | None = None
    actual_cost_usd: float = 0.0
    direct_answer: str = ""

    def summary(self) -> str:
        lines = [
            f"# Run {self.run_id}",
            f"Task: {self.task}",
            f"Lane: {self.routing.lane}  ·  Recipe: {self.routing.recipe}  ·  Profile: {self.routing.quality_profile}",
            f"Workflow: {self.routing.workflow}",
            f"Final decision: {self.final_decision}",
            f"Next owner: {self.next_owner}",
            "",
            "## Handoffs",
        ]
        for h in self.handoffs:
            lines.append(f"- {h.sender} → {h.receiver}: {h.decision}")
        return "\n".join(lines)


def _make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]


def _build_user_message(routing: Routing, prior: list[Handoff], my_role: str, gate_section: str = "", decisions_section: str = "") -> str:
    """Compact, vendor-neutral prompt body containing routing + prior handoffs + gates."""
    parts = [
        "## Task brief",
        "",
        routing.task,
        "",
        "## Routing (decided by AgentCrew's classifier)",
        "",
        f"- lane: {routing.lane}",
        f"- intent: {routing.intent}",
        f"- risk: {routing.risk}",
        f"- recipe: {routing.recipe}",
        f"- quality profile: {routing.quality_profile}",
        f"- workflow: {routing.workflow}",
    ]
    if routing.gates:
        parts.append("- gates: " + ", ".join(routing.gates))
    if routing.specialists:
        parts.append("- specialists: " + ", ".join(routing.specialists))
    parts += ["", "## Your role", f"You are the **{my_role}** in this run.", ""]
    if decisions_section:
        parts += [decisions_section, ""]
    if gate_section:
        parts += [gate_section, ""]
    if prior:
        parts += ["## Prior handoffs (read-only)", ""]
        for h in prior:
            parts.append(h.render_markdown())
    else:
        parts += ["## Prior handoffs", "(none — you are the first acting role)", ""]
    parts += [
        "",
        "Begin your work now. Call `submit_handoff` exactly once when you finish.",
    ]
    return "\n".join(parts)


def _run_role(
    *,
    agent: Agent,
    routing: Routing,
    prior: list[Handoff],
    valid_receivers: list[str],
    project_dir: Path,
    provider: Provider,
    root: AgentCrewRoot,
    decisions_section: str = "",
) -> tuple[AgentRun, Handoff | None]:
    tools = build_tools(role=agent.role, project_root=project_dir)
    schema = submit_handoff_input_schema(agent.role, valid_receivers)
    gate_texts = load_gates_for_role(root, agent.role, routing.gates)
    run = provider.run_agent(
        role=agent.role,
        system_prompt=agent.system_prompt(),
        user_message=_build_user_message(routing, prior, agent.role, render_gate_section(gate_texts), decisions_section),
        tools=tools,
        model=agent.model,
        max_tokens=agent.max_tokens,
        max_iterations=agent.max_iterations,
        submit_tool_name="submit_handoff",
        submit_tool_description=(
            "Submit the final handoff artifact for this turn, per the methodology's "
            "protocols/handoff-format.md. Call exactly once when done."
        ),
        submit_tool_schema=schema,
    )
    if run.submission is None:
        return run, None
    return run, Handoff(**{**run.submission, "model": agent.model})


def _git_status_short(project_dir: Path) -> str | None:
    """Return git status output, or None when project_dir is not a git worktree."""
    result = subprocess.run(
        ["git", "-C", str(project_dir), "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def run(
    *,
    task: str,
    project_dir: Path,
    root: AgentCrewRoot,
    provider: Provider,
    model_for_role: dict[str, str],
    routing_approver: RoutingApprover = auto_approve,
    risk_acceptor: RiskAcceptor = require_explicit_risk_acceptance,
    cost_approver: CostApprover = auto_approve_cost,
    state_root: Path | None = None,
    cwd_for_classifier: str | None = None,
) -> TeamRun:
    """Classify → human gate → cost gate → execute the workflow → return TeamRun.

    Three human gates:
      - routing_approver: shown the Routing before any role runs.
      - cost_approver: shown the cost estimate when warn/block thresholds hit.
      - risk_acceptor: shown on critical-risk routes before the role that
        sits after the methodology's mid-workflow 'Human decision' marker.
    """

    project_dir = project_dir.resolve()
    _run_start_t = _time.monotonic()
    routing = classify(root, task=task, project=cwd_for_classifier or str(project_dir))

    # Apply .agentcrew/config.yaml overrides. The config can only TIGHTEN safety
    # (escalate profile, add specialists, set models). It cannot remove gates
    # or specialists the classifier picked, and it cannot bypass human gates.
    project_config = ProjectConfig.load(project_dir)
    if project_config is not None:
        _apply_project_config(routing, project_config, project_dir, model_for_role)

    run_id = _make_run_id()
    state = TeamRun(
        run_id=run_id,
        task=task,
        project_dir=project_dir,
        run_dir=project_dir / ".agent-state" / "runs" / run_id,
        routing=routing,
    )

    # Direct Answer Mode: the classifier flagged this as advisory. Invoke
    # the Advisor (per agent-team/agents/advisor.md) to actually answer the
    # user. Per Direct Answer Mode, do not create .agent-state artifacts.
    if routing.is_direct_answer():
        advisor_model = model_for_role.get("Advisor")
        if not advisor_model:
            # Without a model we just surface the routing — same as before.
            state.final_decision = "direct_answer_or_advisory"
            state.next_owner = "human"
            return state

        advisor_agent = build_agent(root, "Advisor", advisor_model)
        advisor_run = _run_advisor(
            agent=advisor_agent,
            routing=routing,
            project_dir=project_dir,
            provider=provider,
        )
        state.agent_runs.append(advisor_run)
        if advisor_run.submission is None or not advisor_run.submission.get("answer"):
            state.final_decision = "direct_answer_or_advisory_protocol_failure"
            state.next_owner = "human"
            return state

        answer = advisor_run.submission["answer"]
        state.direct_answer = answer
        state.final_decision = "answered"
        state.next_owner = "human"
        return state

    layout = build_layout(project_dir) if state_root is None else _custom_layout(state_root)
    layout.state_dir.mkdir(parents=True, exist_ok=True)
    run_dir = layout.run_dir(run_id)
    state.run_dir = run_dir

    # Load decisions ONCE for this run. Every role sees the same text.
    decisions_section = render_decisions_section(load_recent_decisions(layout.decisions, limit=10))

    write_current_task(
        layout,
        task=task,
        routing=routing,
        owner=routing.starting_role or "Human",
    )
    write_routing(layout, run_dir, routing)

    # Human gate on the routing.
    if not routing_approver(routing):
        state.final_decision = "routing_rejected_by_human"
        state.next_owner = "human"
        (run_dir / "summary.md").write_text(state.summary())
        return state

    # Build the ordered acting roles from the workflow string.
    acting = routing.acting_roles_in_order()
    if not acting:
        state.final_decision = "no_acting_roles"
        state.next_owner = "human"
        (run_dir / "summary.md").write_text(state.summary())
        return state

    # ---- Cost gate ---------------------------------------------------------
    # Estimate before any LLM call so the user can decline a surprise spend.
    # If config has thresholds set to 0, the gate is effectively skipped.
    role_file_chars: dict[str, int] = {}
    gate_section_chars: dict[str, int] = {}
    max_tokens_per_role: dict[str, int] = {}
    for role in acting:
        try:
            role_file_chars[role] = len(root.role_file(role).read_text())
        except FileNotFoundError:
            role_file_chars[role] = 2000  # estimate when missing
        gate_texts = load_gates_for_role(root, role, routing.gates)
        gate_section_chars[role] = len(render_gate_section(gate_texts))
        max_tokens_per_role[role] = 8192  # see Agent.max_tokens default
    estimate = estimate_run(
        routing=routing,
        acting_roles=acting,
        model_for_role=model_for_role,
        role_file_chars=role_file_chars,
        gate_section_chars_for_role=gate_section_chars,
        max_tokens_per_role=max_tokens_per_role,
    )
    state.cost_estimate = estimate
    budget_status = load_daily_so_far(
        project_dir,
        daily_cap_usd=(project_config.budget.daily_max_usd if project_config else 0.0),
    )
    gate = decide_cost_gate(
        estimate,
        budget_status,
        per_run_warn_usd=(project_config.budget.per_run_warn_usd if project_config else 0.0),
        per_run_block_usd=(project_config.budget.per_run_block_usd if project_config else 0.0),
    )
    (run_dir / "cost-estimate.json").write_text(
        json.dumps(
            {
                "estimate": estimate.to_dict(),
                "daily_so_far_usd": budget_status.daily_so_far_usd,
                "daily_cap_usd": budget_status.daily_cap_usd,
                "warn": gate.warn,
                "block": gate.block,
                "reason": gate.reason,
            },
            indent=2,
        )
    )
    if gate.warn or gate.block:
        if not cost_approver(gate):
            state.final_decision = "cost_rejected_by_human" if gate.block else "cost_warn_rejected_by_human"
            state.next_owner = "human"
            (run_dir / "summary.md").write_text(state.summary())
            return state

    # Split off trailing specialists for parallel execution. They depend
    # only on the primary roles' handoffs, not on each other, so running
    # them concurrently is safe and substantially faster on critical-risk
    # routes that pick multiple specialists.
    primary_acting, trailing_specialists = _split_trailing_specialists(acting, routing.specialists)

    rework_counts: dict[str, int] = {}
    REWORK_LIMIT = 1

    # Resolve where the mid-workflow human-decision gate sits (if any). On
    # critical-risk routes, we pause before this role until the human accepts.
    mid_gate_role = (
        routing.role_after_mid_workflow_human_gate()
        if routing.has_mid_workflow_human_gate()
        else None
    )
    mid_gate_acknowledged = False

    idx = 0
    while idx < len(primary_acting):
        role = primary_acting[idx]

        # Mid-workflow human-decision gate (per the methodology's critical-risk routes).
        if mid_gate_role and role == mid_gate_role and not mid_gate_acknowledged:
            if not risk_acceptor(routing, role):
                state.final_decision = "mid_workflow_human_decision_rejected"
                state.next_owner = "human"
                break
            mid_gate_acknowledged = True
            from .state import append_human_decision

            append_human_decision(
                layout,
                f"- {datetime.now(timezone.utc).isoformat(timespec='seconds')} — accepted critical risk before {role}",
            )

        model = model_for_role.get(role)
        if not model:
            state.final_decision = f"model_missing_for_role:{role}"
            state.next_owner = "human"
            break
        try:
            agent = build_agent(root, role, model)
        except FileNotFoundError as exc:
            state.final_decision = f"role_file_missing:{role}"
            state.next_owner = "human"
            (run_dir / "error.md").write_text(str(exc))
            break

        tester_status_before = _git_status_short(project_dir) if role == "Tester" else None

        # Receivers this role may name in its handoff: any acting role plus Human.
        valid_receivers = list({*acting, *trailing_specialists, "Human"})
        agent_run, handoff = _run_role(
            agent=agent,
            routing=routing,
            prior=state.handoffs,
            valid_receivers=valid_receivers,
            project_dir=project_dir,
            provider=provider,
            root=root,
            decisions_section=decisions_section,
        )
        state.agent_runs.append(agent_run)

        if role == "Tester" and tester_status_before is not None:
            tester_status_after = _git_status_short(project_dir)
            if tester_status_after != tester_status_before:
                state.final_decision = "tester_modified_worktree"
                state.next_owner = "human"
                (run_dir / "error.md").write_text(
                    "Tester role modified the git worktree during validation. "
                    "Route this back to Developer or approve the generated artifacts explicitly.\n"
                )
                break

        if handoff is None:
            state.final_decision = "protocol_failure"
            state.next_owner = "human"
            (run_dir / "error.md").write_text(
                f"{role} did not submit a valid handoff.\n"
            )
            break

        state.handoffs.append(handoff)
        write_handoff(layout, run_dir, handoff)

        # Blocking decisions stop the run completely — no further roles or
        # specialists may execute.
        if handoff.decision in BLOCKING_DECISIONS:
            state.final_decision = handoff.decision
            state.next_owner = "human"
            break

        # Approval decisions ("ready_for_human_approval", etc.) mean THIS role
        # thinks the work is done — but config-required specialists and
        # remaining workflow roles must still run. So we advance the loop;
        # the final decision will be set after specialists complete.

        if handoff.decision in REWORK_DECISIONS:
            if idx == 0:
                state.final_decision = "rework_at_start"
                state.next_owner = "human"
                break
            rework_counts[role] = rework_counts.get(role, 0) + 1
            if rework_counts[role] > REWORK_LIMIT:
                state.final_decision = f"rework_limit_exceeded:{role}"
                state.next_owner = "human"
                break
            idx -= 1
            continue

        idx += 1
    else:
        # Primary workflow finished naturally — now run trailing specialists
        # in parallel. They all see the same `state.handoffs` (read-only) and
        # produce handoffs independently.
        if trailing_specialists:
            spec_results = _run_specialists_parallel(
                specialists=trailing_specialists,
                routing=routing,
                prior=list(state.handoffs),
                valid_receivers=list({*acting, "Human"}),
                project_dir=project_dir,
                provider=provider,
                root=root,
                model_for_role=model_for_role,
                decisions_section=decisions_section,
            )
            for role, agent_run, handoff in spec_results:
                state.agent_runs.append(agent_run)
                if handoff is None:
                    state.final_decision = f"specialist_protocol_failure:{role}"
                    state.next_owner = "human"
                    (run_dir / "error.md").write_text(
                        f"Specialist {role} did not submit a valid handoff.\n"
                    )
                    break
                state.handoffs.append(handoff)
                write_handoff(layout, run_dir, handoff)
                # A blocking decision from any specialist stops the rest.
                if handoff.decision in BLOCKING_DECISIONS:
                    state.final_decision = handoff.decision
                    state.next_owner = "human"
                    break
        if not state.final_decision:
            # Pick the most informative terminal decision: prefer an APPROVAL
            # decision (the role explicitly says ready); fall back to the
            # last handoff's decision otherwise.
            for h in reversed(state.handoffs):
                if h.decision in APPROVAL_DECISIONS:
                    state.final_decision = h.decision
                    break
            else:
                state.final_decision = (
                    state.handoffs[-1].decision if state.handoffs else "no_handoffs"
                )
            state.next_owner = "human"

    # ---- Post-run cost accounting -----------------------------------------
    # Sum actual provider usage across all roles; record to the daily log.
    # Map each agent_run back to the role that produced it (same order
    # they appended to state.agent_runs and state.handoffs).
    actual_total = 0.0
    for ar, hf in zip(state.agent_runs, state.handoffs):
        if hasattr(ar, "usage") and ar.usage:
            actual_total += actual_cost_from_usage(hf.model or "", ar.usage)
    state.actual_cost_usd = actual_total
    if actual_total > 0:
        record_run_cost(project_dir, run_id=run_id, cost_usd=actual_total)
    (run_dir / "cost-actual.json").write_text(
        json.dumps(
            {
                "actual_cost_usd": round(actual_total, 6),
                "estimated_cost_usd": round(estimate.total_usd, 6),
                "daily_total_after": round(budget_status.daily_so_far_usd + actual_total, 6),
            },
            indent=2,
        )
    )

    (run_dir / "summary.md").write_text(state.summary())

    # Opt-in anonymous telemetry — per-run aggregate metrics, never task content.
    emit_run_event(
        project_dir,
        enabled=bool(project_config and project_config.telemetry_enabled),
        run_id=run_id,
        lane=routing.lane,
        recipe=routing.recipe,
        risk=routing.risk,
        quality_profile=routing.quality_profile,
        acting_roles_count=len(acting) if 'acting' in dir() else 0,
        specialists_count=len(routing.specialists),
        gates_count=len(routing.gates),
        final_decision=state.final_decision,
        next_owner=state.next_owner,
        estimated_cost_usd=estimate.total_usd if 'estimate' in dir() else 0.0,
        actual_cost_usd=state.actual_cost_usd,
        duration_seconds=_time.monotonic() - _run_start_t,
        models_by_role=model_for_role,
    )

    return state


def _split_trailing_specialists(
    acting: list[str], specialists: list[str]
) -> tuple[list[str], list[str]]:
    """Split acting into (primary, trailing_specialists).

    Trailing specialists = the longest suffix of `acting` where every role
    is in `specialists`. They can run concurrently because they all depend
    only on the primary workflow's handoffs, not on each other.

    If specialists are interleaved (e.g. Developer -> Security Reviewer ->
    Tester), only the trailing run is parallelized; earlier specialists
    stay in the primary list and run serially.
    """
    specs = set(specialists)
    if not specs:
        return list(acting), []
    cutoff = len(acting)
    while cutoff > 0 and acting[cutoff - 1] in specs:
        cutoff -= 1
    return acting[:cutoff], acting[cutoff:]


def _run_specialists_parallel(
    *,
    specialists: list[str],
    routing: Routing,
    prior: list[Handoff],
    valid_receivers: list[str],
    project_dir: Path,
    provider: Provider,
    root: AgentCrewRoot,
    model_for_role: dict[str, str],
    decisions_section: str = "",
) -> list[tuple[str, AgentRun, Handoff | None]]:
    """Run each trailing specialist in its own thread.

    Returns results in the same order as the input `specialists` list, so
    persisted artifacts are deterministic regardless of which thread finished
    first.

    Note: this assumes the Provider implementation is thread-safe. The
    bundled MockProvider and the HTTP-based providers (OpenAI/local) are.
    Common provider SDK clients are thread-safe enough for this use.
    """
    def _one(role: str) -> tuple[str, AgentRun, Handoff | None]:
        model = model_for_role.get(role)
        if not model:
            empty_run = AgentRun()
            empty_run.stop_reason = f"model_missing_for_role:{role}"
            return role, empty_run, None
        try:
            agent = build_agent(root, role, model)
        except FileNotFoundError:
            empty_run = AgentRun()
            empty_run.stop_reason = f"role_file_missing:{role}"
            return role, empty_run, None
        agent_run, handoff = _run_role(
            agent=agent,
            routing=routing,
            prior=prior,
            valid_receivers=valid_receivers,
            project_dir=project_dir,
            provider=provider,
            root=root,
            decisions_section=decisions_section,
        )
        return role, agent_run, handoff

    if len(specialists) == 1:
        return [_one(specialists[0])]

    max_workers = min(len(specialists), 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit in input order, collect by future-to-index for deterministic ordering.
        futures = {executor.submit(_one, role): i for i, role in enumerate(specialists)}
        results: list[tuple[str, AgentRun, Handoff | None] | None] = [None] * len(specialists)
        for future in futures:
            idx = futures[future]
            results[idx] = future.result()
    return [r for r in results if r is not None]


def _submit_answer_schema() -> dict:
    """JSON schema for the Advisor's submit_answer tool (Direct Answer Mode)."""
    return {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": (
                    "Your direct answer to the user's question. Plain Markdown. "
                    "Be specific and concrete. Cite files/lines from the project "
                    "when relevant. No fluff."
                ),
                "minLength": 1,
                "maxLength": 8000,
            },
        },
        "required": ["answer"],
    }


def _build_advisor_user_message(task: str) -> str:
    return (
        "## User's question\n\n"
        f"{task}\n\n"
        "the classifier routed this to **Direct Answer Mode** — the user is "
        "asking a question, not requesting code changes. Read just enough of "
        "the project to give a useful answer, then call `submit_answer`.\n"
    )


def _run_advisor(
    *,
    agent: Agent,
    routing: Routing,
    project_dir: Path,
    provider: Provider,
) -> AgentRun:
    """Run the Advisor for Direct Answer Mode — no handoff, just a written answer."""
    tools = build_tools(role="Advisor", project_root=project_dir)
    return provider.run_agent(
        role="Advisor",
        system_prompt=agent.system_prompt(),
        user_message=_build_advisor_user_message(routing.task),
        tools=tools,
        model=agent.model,
        max_tokens=agent.max_tokens,
        max_iterations=agent.max_iterations,
        submit_tool_name="submit_answer",
        submit_tool_description=(
            "Submit your direct answer to the user's question. "
            "Call exactly once when you are done."
        ),
        submit_tool_schema=_submit_answer_schema(),
    )


def _apply_project_config(
    routing: Routing,
    config: ProjectConfig,
    project_dir: Path,
    model_for_role: dict[str, str],
) -> None:
    """Apply project-level overrides to the routing in-place.

    Safety direction: the config can only tighten, never widen. We escalate
    the profile, add specialists, and supply per-role models — we never
    remove specialists or downgrade the profile.
    """
    # 1. Recipe → profile override (or global profile override).
    new_profile = config.profile_for_recipe(routing.recipe, routing.quality_profile)
    if new_profile != routing.quality_profile:
        routing.reasons.append(
            f"config override: profile {routing.quality_profile} -> {new_profile} "
            f"(from .agentcrew/config.yaml)"
        )
        routing.quality_profile = new_profile

    # 2. Required-specialists rules — add (never remove) specialists when
    # project files match a glob.
    extra = config.required_specialists_for_project(project_dir)
    added = []
    for role in extra:
        if role not in routing.specialists:
            routing.specialists.append(role)
            added.append(role)
    if added:
        routing.reasons.append(
            f"config override: added specialists {added} for matching paths"
        )

    # 3. Per-role models from config become defaults — CLI flags still win,
    # so we only fill in roles that the caller hasn't already supplied.
    for role, model in config.models.items():
        if role not in model_for_role:
            model_for_role[role] = model


def _custom_layout(state_root: Path) -> StateLayout:
    """Used by tests that point .agent-state/ somewhere else."""
    state_root = state_root.resolve()
    return StateLayout(
        root=state_root.parent,
        state_dir=state_root,
        sessions_dir=state_root / "sessions",
        runs_dir=state_root / "runs",
        current_task=state_root / "current-task.md",
        handoff=state_root / "handoff.md",
        decisions=state_root / "decisions.md",
        human_decisions=state_root / "human-decisions.md",
        memory=state_root / "memory.md",
    )
