"""Routing — wraps the classifier script as a typed Python interface.

The classifier already classifies the request deterministically: intent, risk, lane,
quality profile, recipe, starting role, next roles, reviewers, specialists,
skills, gates, human decisions, files to load, reasons.

This module shells out to that classifier and returns a typed Routing
dataclass. The orchestrator consumes it directly — no LLM call needed for
the routing decision itself.

For ambiguous classifications, the orchestrator can optionally invoke an
Advisor LLM call (per agent-team/playbooks/request-routing.md), but that
is REFINEMENT of the classifier's output, never a replacement for it.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field

from .agentcrew_root import AgentCrewRoot


# Lane string vocabulary the classifier emits.
class Lane:
    DIRECT_ANSWER = "Direct Answer Mode"
    FAST = "Fast Lane"
    FAST_WITH_REVIEW = "Fast Lane with required review or Full Lane if unclear"
    FULL = "Full Lane"
    FULL_PLUS_DECISION = "Full Lane plus explicit human decision"


@dataclass
class Routing:
    """The structured output of the classifier script.

    Field names mirror the YAML keys exactly so a maintainer reading this
    can cross-reference agent-team/tools/classify-task.sh.
    """

    task: str
    project: str
    intent: str
    risk: str
    lane: str
    quality_profile: str
    recipe: str
    starting_role: str
    workflow: str
    next_roles: list[str] = field(default_factory=list)
    reviewers: list[str] = field(default_factory=list)
    specialists: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    gates: list[str] = field(default_factory=list)
    human_decisions: list[str] = field(default_factory=list)
    files_to_load: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def is_direct_answer(self) -> bool:
        return self.lane == Lane.DIRECT_ANSWER

    def requires_human_decision_on_routing(self) -> bool:
        return self.lane == Lane.FULL_PLUS_DECISION

    def workflow_roles(self) -> list[str]:
        """Parse 'Developer -> Tester -> Human' into ['Developer', 'Tester', 'Human']."""
        return [step.strip() for step in self.workflow.split("->") if step.strip()]

    def acting_roles_in_order(self) -> list[str]:
        """Roles that actually act, in the order the workflow runs.

        Drops 'Human' (terminal gate). For roles guarded by conditionals
        ('Reviewer if risk is meaningful'), evaluates the condition
        against this Routing and includes the role only if it holds.
        Unknown conditions default to include (conservative).

        The 'Specialist Reviewer' placeholder in workflow strings is
        expanded into the actual specialists listed by the classifier.
        Explicitly repeated roles remain separate workflow phases.
        Specialists named in `self.specialists` that don't appear in the
        workflow at all are appended after the primary roles, per
        agent-team/playbooks/specialist-review-routing.md.
        """
        out: list[str] = []

        def _add(role: str, *, deduplicate: bool = False) -> None:
            # 'Human' and 'Human decision' are events in workflow strings,
            # not actors. The orchestrator handles human gates separately.
            if role in {"Human", "Human decision"}:
                return
            if role and (not deduplicate or role not in out):
                out.append(role)

        for step in self.workflow_roles():
            if step in {"Human", "Human decision"}:
                continue
            m = re.match(r"^(.+?)(?:\s+if\s+(.+))?$", step.strip())
            if not m:
                continue
            role = m.group(1).strip()
            condition = m.group(2)

            if role == "Specialist Reviewer":
                # Placeholder — expand to the concrete specialists the classifier picked.
                if condition and not _evaluate_condition(condition, self):
                    continue
                for specialist in self.specialists:
                    _add(specialist, deduplicate=True)
                continue

            if condition and not _evaluate_condition(condition, self):
                continue
            _add(role)

        # Specialists named by the classifier but absent from the workflow
        # still need to run (per specialist-review-routing.md). Append after
        # the primary roles so they see prior handoffs.
        for specialist in self.specialists:
            _add(specialist, deduplicate=True)

        return out

    def has_mid_workflow_human_gate(self) -> bool:
        """True when the classifier inserts a 'Human decision' mid-workflow.

        Appears on critical-risk routes ('Full Lane plus explicit human
        decision'). The orchestrator pauses execution before the role that
        follows the gate; see role_after_mid_workflow_human_gate().
        """
        return any(step.strip() == "Human decision" for step in self.workflow_roles())

    def role_after_mid_workflow_human_gate(self) -> str | None:
        """Return the first acting role that follows 'Human decision' in the
        workflow string, or None when there is no mid-workflow gate.

        The orchestrator pauses BEFORE invoking this role on critical-risk
        runs, so the human gets to accept risk before any implementation
        starts. The Advisor and Idea Consultant phases (which sit before
        'Human decision') still run; this is the second pause point.
        """
        steps = self.workflow_roles()
        try:
            idx = next(i for i, s in enumerate(steps) if s.strip() == "Human decision")
        except StopIteration:
            return None
        # Walk forward to the first step that's an actual acting role.
        for step in steps[idx + 1:]:
            stripped = step.strip()
            if stripped in {"Human", "Human decision"}:
                continue
            m = re.match(r"^(.+?)(?:\s+if\s+(.+))?$", stripped)
            if not m:
                continue
            role = m.group(1).strip()
            if role == "Specialist Reviewer":
                # The placeholder expands to specialists; pause before the first one.
                if self.specialists:
                    return self.specialists[0]
                continue
            condition = m.group(2)
            if condition and not _evaluate_condition(condition, self):
                continue
            return role
        return None


_MEANINGFUL_RISK = {"medium", "high", "critical"}


def _evaluate_condition(condition: str, routing: "Routing") -> bool:
    """Best-effort evaluation of the classifier's common 'if ...' conditional clauses.

    Known patterns (lowercased):
      - 'risk is meaningful'         → risk in {medium, high, critical}
      - 'release risk is meaningful' → same
      - 'needed' / 'triggered'       → specialists list is non-empty
      - 'validation evidence is missing' → unknown — default include
      - 'behavior claims changed'    → unknown — default include
      - 'expected behavior'/'decision needed' → unknown — default include
      - 'defect is confirmed'        → unknown — default include
      - 'reproduction is needed'     → unknown — default include
      - 'implementation follows'     → True iff Developer is already in workflow
      - anything else                → default include (conservative)

    Returning True means 'include this role'. Returning False skips it.
    Unknown patterns return True so we never silently drop a role the classifier's
    spec might require.
    """
    c = condition.strip().lower()
    if "risk is meaningful" in c or "release risk is meaningful" in c:
        return routing.risk in _MEANINGFUL_RISK
    if c.endswith("needed") or c == "needed" or "if needed" in c or "triggered" in c:
        return len(routing.specialists) > 0
    if "implementation follows" in c:
        roles = [s.strip() for s in routing.workflow.split("->") if s.strip()]
        return "Developer" in roles
    return True


def classify(root: AgentCrewRoot, task: str, project: str) -> Routing:
    """Invoke the classifier script and parse its YAML output into Routing."""
    if not root.classifier.exists():
        raise FileNotFoundError(f"Classifier missing: {root.classifier}")
    result = subprocess.run(
        [str(root.classifier), "--project", project, "--task", task],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"classify-task.sh failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return _parse_yaml(result.stdout)


# the classifier emits a constrained YAML dialect: a single top-level key
# `task_classification` with scalar string values (single-quoted) and list
# values formatted as `- 'value'`. We parse just enough of it to populate
# Routing — no general YAML lib needed (and avoids adding a dep).
_SCALAR_RX = re.compile(r"^  ([a-z_]+): '(.*)'$")
_LIST_KEY_RX = re.compile(r"^  ([a-z_]+):$")
_LIST_ITEM_RX = re.compile(r"^    - (?:'(.*)'|none)$")


def _unquote(value: str) -> str:
    return value.replace("''", "'")


def _parse_yaml(text: str) -> Routing:
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "task_classification:":
        raise ValueError(
            f"Unexpected classifier output (missing 'task_classification:' header):\n{text[:500]}"
        )

    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {}
    current_list: list[str] | None = None

    for raw in lines[1:]:
        if not raw.strip():
            current_list = None
            continue

        m = _SCALAR_RX.match(raw)
        if m:
            scalars[m.group(1)] = _unquote(m.group(2))
            current_list = None
            continue

        m = _LIST_KEY_RX.match(raw)
        if m:
            current_list = []
            lists[m.group(1)] = current_list
            continue

        m = _LIST_ITEM_RX.match(raw)
        if m and current_list is not None:
            value = m.group(1)
            if value is None:
                # Literal 'none' marker — record as empty list
                continue
            current_list.append(_unquote(value))
            continue

        # Lines like `  note: '...'` (the trailing note) we accept silently
        if raw.startswith("  note:"):
            current_list = None
            continue
        # Unknown line — ignore rather than fail, since the classifier
        # may add new fields. We just won't surface them.
        current_list = None

    def _scalar(key: str, required: bool = True, default: str = "") -> str:
        if key not in scalars:
            if required:
                raise ValueError(f"classify-task.sh output missing required key: {key}")
            return default
        return scalars[key]

    return Routing(
        task=_scalar("task"),
        project=_scalar("project"),
        intent=_scalar("intent"),
        risk=_scalar("risk"),
        lane=_scalar("lane"),
        quality_profile=_scalar("quality_profile"),
        recipe=_scalar("recipe"),
        starting_role=_scalar("starting_role"),
        workflow=_scalar("workflow"),
        next_roles=lists.get("next_roles", []),
        reviewers=lists.get("reviewers", []),
        specialists=lists.get("specialists", []),
        skills=lists.get("skills", []),
        gates=lists.get("gates", []),
        human_decisions=lists.get("human_decisions", []),
        files_to_load=lists.get("files_to_load", []),
        reasons=lists.get("reasons", []),
    )


def render_markdown(r: Routing) -> str:
    """Render Routing as the methodology's templates/task-routing.md shape."""
    bullet = lambda xs: "\n".join(f"- {x}" for x in xs) if xs else "- none"
    return (
        "# Task Routing\n\n"
        "## Route\n\n"
        f"- lane: {r.lane}\n"
        f"- starting role: {r.starting_role}\n"
        f"- quality profile: {r.quality_profile}\n"
        f"- recipe: {r.recipe}\n"
        f"- next roles: {', '.join(r.next_roles) or 'none'}\n\n"
        "## Why\n\n"
        f"- risk: {r.risk}\n"
        f"- intent: {r.intent}\n"
        f"- reasons:\n{bullet(r.reasons)}\n\n"
        "## Specialists\n\n"
        f"{bullet(r.specialists)}\n\n"
        "## Skills\n\n"
        f"{bullet(r.skills)}\n\n"
        "## Gates\n\n"
        f"{bullet(r.gates)}\n\n"
        "## Human Decisions\n\n"
        f"{bullet(r.human_decisions)}\n\n"
        "## Files To Load\n\n"
        f"{bullet(r.files_to_load)}\n"
    )
