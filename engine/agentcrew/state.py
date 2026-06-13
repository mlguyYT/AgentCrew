"""State artifacts — implements the methodology's protocols/state-artifacts.md.

The methodology specifies a fixed set of files under `.agent-state/`. the engine's persistence
writes to those files, with the same purposes the methodology documents. This module
is the only place that decides where things go on disk.

The schema (from state-artifacts.md):

    .agent-state/
      sessions/
      current-task.md
      project-preset.md
      task-brief.md
      work-plan.md
      readiness-report.md
      pr-pack.md
      decisions.md
      human-decisions.md
      handoff.md
      test-report.md
      review-report.md
      security-review-report.md
      ux-design-review-report.md
      documentation-report.md
      support-triage-report.md
      release-report.md
      memory.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .handoff import Handoff
from .routing import Routing, render_markdown as render_routing_md


# Per-role report files defined by state-artifacts.md. Roles whose
# handoff content should land in one of these get routed automatically.
_REPORT_FILE_BY_ROLE: dict[str, str] = {
    "Tester": "test-report.md",
    "Reviewer": "review-report.md",
    "Security Reviewer": "security-review-report.md",
    "UX / Design Reviewer": "ux-design-review-report.md",
    "Documentation Agent": "documentation-report.md",
    "Support Triage Agent": "support-triage-report.md",
    "Release Manager": "release-report.md",
    "LLM Agent": "llm-report.md",
    "Researcher Agent": "research-report.md",
    "CNN Agent": "cnn-report.md",
    "Skill Validator": "skill-validation-report.md",
}


@dataclass(frozen=True)
class StateLayout:
    """Resolved paths for one run's state artifacts."""

    root: Path
    state_dir: Path
    sessions_dir: Path
    runs_dir: Path
    current_task: Path
    handoff: Path
    decisions: Path
    human_decisions: Path
    memory: Path

    def role_report_path(self, role: str) -> Path | None:
        name = _REPORT_FILE_BY_ROLE.get(role)
        return (self.state_dir / name) if name else None

    def run_dir(self, run_id: str) -> Path:
        d = self.runs_dir / run_id
        d.mkdir(parents=True, exist_ok=True)
        return d


def build_layout(project_dir: Path) -> StateLayout:
    project_dir = project_dir.resolve()
    state_dir = (project_dir / ".agent-state").resolve()
    return StateLayout(
        root=project_dir,
        state_dir=state_dir,
        sessions_dir=state_dir / "sessions",
        runs_dir=state_dir / "runs",
        current_task=state_dir / "current-task.md",
        handoff=state_dir / "handoff.md",
        decisions=state_dir / "decisions.md",
        human_decisions=state_dir / "human-decisions.md",
        memory=state_dir / "memory.md",
    )


def write_current_task(layout: StateLayout, *, task: str, routing: Routing, owner: str, status: str = "intake", next_action: str = "Begin role workflow.") -> Path:
    """Write `.agent-state/current-task.md` per the template.

    Field set comes verbatim from agent-team/templates/current-task.md.
    """
    layout.state_dir.mkdir(parents=True, exist_ok=True)
    body = (
        "# Current Task\n\n"
        f"## Title\n{_short_title(task)}\n\n"
        f"## Request\n{task}\n\n"
        f"## Intent\n{routing.intent}\n\n"
        f"## Lane\n{routing.lane}\n\n"
        f"## Risk\n{routing.risk}\n\n"
        f"## Quality Profile\n{routing.quality_profile}\n\n"
        f"## Recipe\n{routing.recipe}\n\n"
        f"## Owner\n{owner}\n\n"
        f"## Workflow\n{routing.workflow}\n\n"
        f"## Acceptance Criteria\n- (provisional — Tester to confirm)\n\n"
        f"## Status\n{status}\n\n"
        f"## Next Action\n{next_action}\n\n"
        f"## Open Questions\n"
        + ("\n".join(f"- {q}" for q in routing.human_decisions) if routing.human_decisions else "None.")
        + "\n\n"
        "## Safety\n"
        "No secrets, tokens, raw customer data, sensitive production data, "
        "personal identifiers, local machine paths, private key paths, deploy-key paths, "
        "long logs, or hidden reasoning traces.\n"
    )
    layout.current_task.write_text(body)
    return layout.current_task


def write_routing(layout: StateLayout, run_dir: Path, routing: Routing) -> Path:
    """Persist the routing per the methodology's templates/task-routing.md shape."""
    p = run_dir / "task-routing.md"
    p.write_text(render_routing_md(routing))
    (run_dir / "task-routing.json").write_text(
        _routing_to_json(routing)
    )
    return p


def write_handoff(layout: StateLayout, run_dir: Path, handoff: Handoff) -> Path:
    """Append handoff to the run dir AND update current handoff + per-role report."""
    from .handoff import persist as _persist

    md_path = _persist(handoff, run_dir, layout.handoff)
    # Also mirror to the per-role report file when state-artifacts.md defines one for the sender.
    report_path = layout.role_report_path(handoff.sender)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(handoff.render_markdown())
    return md_path


def append_decision(layout: StateLayout, line: str) -> None:
    layout.decisions.parent.mkdir(parents=True, exist_ok=True)
    with layout.decisions.open("a") as f:
        f.write(line.rstrip() + "\n")


def append_human_decision(layout: StateLayout, line: str) -> None:
    layout.human_decisions.parent.mkdir(parents=True, exist_ok=True)
    with layout.human_decisions.open("a") as f:
        f.write(line.rstrip() + "\n")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def _short_title(task: str, max_chars: int = 64) -> str:
    cleaned = " ".join(task.split())
    return cleaned[:max_chars] + ("…" if len(cleaned) > max_chars else "")


def _routing_to_json(routing: Routing) -> str:
    """Serialize Routing to JSON without adding a Pydantic dep (it's a dataclass)."""
    import json
    from dataclasses import asdict

    return json.dumps(asdict(routing), indent=2)
