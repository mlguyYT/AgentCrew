"""Execute one bounded role turn and apply role-specific evidence gates."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .agentcrew_root import AgentCrewRoot
from .agents import Agent
from .context_compiler import compile_execution_context
from .execution_evidence import (
    ExecutionRecorder,
    FileFingerprint,
    build_execution_evidence,
    clip_metadata,
    enforce_completion,
)
from .gates import load_gates_for_role, render_gate_section
from .handoff import (
    BLOCKING_DECISIONS,
    REWORK_DECISIONS,
    Handoff,
    submit_handoff_input_schema,
)
from .provider import AgentRun, Provider
from .quality_evidence import (
    build_reviewer_evidence,
    build_tester_evidence,
    enforce_reviewer_completion,
    enforce_tester_completion,
)
from .routing import Routing
from .tools import build_tools


_COMPILED_CONTEXT_ROLES = {"Developer", "Tester", "Reviewer"}
_BEHAVIOR_RECIPES = {"bug-fix", "feature", "refactor", "incident"}


def build_user_message(
    routing: Routing,
    prior: list[Handoff],
    role: str,
    *,
    gate_section: str = "",
    decisions_section: str = "",
    runtime_guidance: str = "",
    evidence_section: str = "",
) -> str:
    """Build a compact prompt from routing, handoffs, and bounded guidance."""

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
    parts += ["", "## Your role", f"You are the **{role}** in this run.", ""]
    if decisions_section:
        parts += [decisions_section, ""]
    if runtime_guidance:
        parts += [runtime_guidance, ""]
    if evidence_section:
        parts += [evidence_section, ""]
    if gate_section:
        parts += [gate_section, ""]
    if prior:
        parts += ["## Prior handoffs (read-only)", ""]
        for handoff in prior:
            parts.append(handoff.render_markdown())
    else:
        parts += [
            "## Prior handoffs",
            "(none - you are the first acting role)",
            "",
        ]
    parts += [
        "",
        "Begin your work now. Call `submit_handoff` exactly once when you finish.",
    ]
    return "\n".join(parts)


def run_role(
    *,
    agent: Agent,
    routing: Routing,
    prior: list[Handoff],
    valid_receivers: list[str],
    project_dir: Path,
    provider: Provider,
    root: AgentCrewRoot,
    decisions_section: str = "",
    developer_status_baseline: str | None = None,
    developer_file_baselines: dict[
        str, FileFingerprint | None
    ] | None = None,
    expected_changed_files: tuple[str, ...] = (),
    git_available: bool = False,
) -> tuple[AgentRun, Handoff | None]:
    """Run one role with bounded context, tools, and observed evidence."""

    tools = build_tools(
        role=agent.role,
        project_root=project_dir,
        review_paths=(
            expected_changed_files if agent.role == "Reviewer" else ()
        ),
    )
    recorder = None
    if agent.role == "Developer":
        recorder = ExecutionRecorder(project_dir, developer_file_baselines)
        tools = recorder.instrument(tools)
    elif agent.role in {"Tester", "Reviewer"}:
        recorder = ExecutionRecorder(project_dir)
        tools = recorder.instrument(tools)

    schema = submit_handoff_input_schema(agent.role, valid_receivers)
    gate_texts = load_gates_for_role(root, agent.role, routing.gates)
    compiled_context = None
    gate_section = render_gate_section(gate_texts)
    if agent.role in _COMPILED_CONTEXT_ROLES:
        compiled_context = compile_execution_context(
            root=root,
            routing=routing,
            role=agent.role,
            gate_texts=gate_texts,
        )
        gate_section = ""

    run = provider.run_agent(
        role=agent.role,
        system_prompt=agent.system_prompt(),
        user_message=build_user_message(
            routing,
            prior,
            agent.role,
            gate_section=gate_section,
            decisions_section=decisions_section,
            runtime_guidance=(
                compiled_context.text if compiled_context else ""
            ),
            evidence_section=_evidence_section(
                agent.role,
                expected_changed_files,
                prior,
            ),
        ),
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
    if compiled_context is not None:
        run.context_fragments = compiled_context.fragment_ids
        run.context_estimated_tokens = compiled_context.estimated_tokens

    handoff = (
        Handoff(**{**run.submission, "model": agent.model})
        if run.submission is not None
        else None
    )
    if recorder is None:
        return run, handoff

    if agent.role == "Developer":
        _apply_developer_evidence(
            run,
            handoff,
            recorder,
            project_dir,
            developer_status_baseline,
        )
    elif agent.role == "Tester":
        _apply_tester_evidence(
            run,
            handoff,
            recorder,
            routing,
            valid_receivers,
        )
    elif agent.role == "Reviewer":
        _apply_reviewer_evidence(
            run,
            handoff,
            recorder,
            expected_changed_files,
            git_available,
        )
    return run, handoff


def git_status_short(project_dir: Path) -> str | None:
    """Return git status output, or None when the project is not a worktree."""

    result = subprocess.run(
        [
            "git",
            "-C",
            str(project_dir),
            "status",
            "--short",
            "--",
            ".",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def _evidence_section(
    role: str,
    expected_changed_files: tuple[str, ...],
    prior: list[Handoff],
) -> str:
    if role not in {"Tester", "Reviewer"}:
        return ""
    paths = [
        clip_metadata(path, 200)
        for path in expected_changed_files[:20]
    ]
    lines = [
        "## Engine-observed scope",
        "",
        "- changed paths: "
        + (", ".join(paths) if paths else "(none recorded)"),
    ]
    if len(expected_changed_files) > len(paths):
        lines.append(
            f"- additional changed paths omitted: {len(expected_changed_files) - len(paths)}"
        )
    validation = [
        f"{handoff.sender}: {handoff.validation_status}"
        for handoff in prior
        if handoff.validation_status
    ][-5:]
    if validation:
        lines.append("- prior validation status: " + "; ".join(validation))
    lines.append("- treat handoff claims as context, not independent proof")
    return "\n".join(lines)


def _apply_developer_evidence(
    run: AgentRun,
    handoff: Handoff | None,
    recorder: ExecutionRecorder,
    project_dir: Path,
    status_baseline: str | None,
) -> None:
    evidence = build_execution_evidence(
        recorder=recorder,
        status_before=status_baseline,
        status_after=git_status_short(project_dir),
    )
    assessment = None
    if (
        handoff is not None
        and handoff.decision not in BLOCKING_DECISIONS
        and handoff.decision not in REWORK_DECISIONS
    ):
        assessment = enforce_completion(evidence, handoff)
    run.observed_changed_files = evidence.observed_changed_files[:200]
    run.execution_evidence = evidence.to_dict(assessment)


def _apply_tester_evidence(
    run: AgentRun,
    handoff: Handoff | None,
    recorder: ExecutionRecorder,
    routing: Routing,
    valid_receivers: list[str],
) -> None:
    evidence = build_tester_evidence(recorder)
    assessment = None
    if handoff is not None and handoff.decision not in BLOCKING_DECISIONS:
        assessment = enforce_tester_completion(
            evidence,
            handoff,
            require_behavior_validation=(
                routing.recipe in _BEHAVIOR_RECIPES
            ),
            developer_available="Developer" in valid_receivers,
        )
    run.validation_evidence = evidence.to_dict(assessment)


def _apply_reviewer_evidence(
    run: AgentRun,
    handoff: Handoff | None,
    recorder: ExecutionRecorder,
    expected_changed_files: tuple[str, ...],
    git_available: bool,
) -> None:
    evidence = build_reviewer_evidence(
        recorder,
        expected_changed_files=expected_changed_files,
    )
    assessment = None
    if handoff is not None:
        assessment = enforce_reviewer_completion(
            evidence,
            handoff,
            git_available=git_available,
        )
    run.review_evidence = evidence.to_dict(assessment)
