"""Handoff artifact — the the schema, as Pydantic.

Mirrors `agent-team/protocols/handoff-format.md` and
`agent-team/templates/compact-handoff.md` exactly. Field names match the methodology's
template; serialization round-trips through the same Markdown shape.

This is intentionally a faithful Python re-statement of the schema, not
a re-imagining. If the methodology template changes, this file moves with it.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# Decisions where the role thinks it's done and ready for human review.
# These do NOT stop the run on their own — if there are trailing specialists
# or required reviewers, they must still run. Required specialists from
# .agentcrew/config.yaml depend on this.
APPROVAL_DECISIONS = frozenset(
    {
        "ready_for_human_approval",
        "ready_for_human_release_review",
        "answered",
    }
)

# Decisions that block the run completely — nothing else may execute.
BLOCKING_DECISIONS = frozenset(
    {
        "blocked",
        "blocked_open_question",
        "rejected_scope",
        "hold_for_fixes",
        "hold_for_pm",
        "needs_human_decision",
    }
)

# Combined: anything that terminates the run (whether via approval or block)
# OR that the human needs to act on. Used by callers that want any human-gate.
HUMAN_GATE_DECISIONS = APPROVAL_DECISIONS | BLOCKING_DECISIONS


# Decisions that route work back to a prior role.
REWORK_DECISIONS = frozenset({"needs_rework", "rework_required"})


class Handoff(BaseModel):
    """The compact handoff artifact per the methodology's protocols/handoff-format.md.

    Required fields (every handoff has these):
      - sender / receiver: role names per agent-team/agents/
      - context: 1–3 bullets, factual
      - decision: one sentence stating the outcome
      - evidence: facts the next agent needs
      - next_action: exactly one action for the next agent
      - open_questions: blockers only, or empty list

    Optional sections ('use only when helpful'):
      - acceptance_criteria
      - files (paths touched or referenced)
      - commands (each with a pass/fail marker)
    """

    sender: str = Field(min_length=1, max_length=64, description="Role producing this handoff")
    receiver: str = Field(min_length=1, max_length=64, description="Role expected to act next ('Human' is valid)")
    decision: str = Field(min_length=1, max_length=400)
    context: list[str] = Field(default_factory=list, max_length=3)
    evidence: list[str] = Field(default_factory=list, max_length=20)
    next_action: str = Field(min_length=1, max_length=300)
    open_questions: list[str] = Field(default_factory=list, max_length=5)

    # Optional sections
    acceptance_criteria: list[str] = Field(default_factory=list, max_length=10)
    files: list[str] = Field(default_factory=list, max_length=20)
    commands: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Each entry should follow the 'command: pass|fail' shape.",
    )
    validation_status: Literal[
        "passed", "failed", "unavailable", "not_applicable"
    ] | None = None
    validation_limitation: str = Field(
        default="",
        max_length=500,
        description=(
            "Why validation is unavailable or not applicable. Actual tool "
            "results override self-reported validation status."
        ),
    )

    # Bookkeeping (not part of the user-visible schema, but useful for traces)
    model: str | None = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    @model_validator(mode="after")
    def require_declared_validation_limitation(self) -> Handoff:
        if (
            self.validation_status in {"unavailable", "not_applicable"}
            and not self.validation_limitation.strip()
        ):
            raise ValueError(
                "validation_limitation is required when validation is "
                "unavailable or not_applicable"
            )
        return self

    def render_markdown(self) -> str:
        """Serialize to the exact Markdown shape the methodology expects in .agent-state/handoff.md."""
        lines = [f"## {self.sender} -> {self.receiver} Handoff", ""]
        lines += ["### Context"]
        if self.context:
            lines += [f"- {c}" for c in self.context]
        else:
            lines += ["- (none)"]
        lines += ["", "### Decision", self.decision, "", "### Evidence"]
        if self.evidence:
            lines += [f"- {e}" for e in self.evidence]
        else:
            lines += ["- (none)"]
        lines += ["", "### Next Action", self.next_action, "", "### Open Questions"]
        if self.open_questions:
            lines += [f"- {q}" for q in self.open_questions]
        else:
            lines += ["None."]
        if self.acceptance_criteria:
            lines += ["", "### Acceptance Criteria"]
            lines += [f"- {a}" for a in self.acceptance_criteria]
        if self.files:
            lines += ["", "### Files"]
            lines += [f"- {f}" for f in self.files]
        if self.commands:
            lines += ["", "### Commands"]
            lines += [f"- {c}" for c in self.commands]
        if self.validation_status:
            lines += ["", "### Validation"]
            lines += [f"- status: {self.validation_status}"]
            if self.validation_limitation:
                lines += [f"- limitation: {self.validation_limitation}"]
        return "\n".join(lines) + "\n"


def submit_handoff_input_schema(sender: str, valid_receivers: list[str]) -> dict:
    """Build the JSON schema for the `submit_handoff` tool the role calls.

    `sender` is pinned via enum so a Developer can't submit a Reviewer handoff.
    `valid_receivers` is similarly constrained to roles + 'Human'.
    """
    schema = Handoff.model_json_schema()
    schema.pop("$defs", None)
    schema["properties"]["sender"] = {"type": "string", "enum": [sender]}
    schema["properties"]["receiver"] = {"type": "string", "enum": valid_receivers}
    schema["required"] = ["sender", "receiver", "decision", "next_action"]
    return schema


def persist(handoff: Handoff, run_dir: Path, current_handoff_path: Path) -> Path:
    """Write the handoff Markdown + JSON sidecar.

    - `run_dir/<slug>.{md,json}` keeps every handoff in the run history.
    - `current_handoff_path` (typically .agent-state/handoff.md) holds the
      latest one per the methodology's protocols/state-artifacts.md.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{handoff.sender.lower().replace(' ', '_').replace('/', '_')}-to-{handoff.receiver.lower().replace(' ', '_').replace('/', '_')}"
    md_path = run_dir / f"{slug}.md"
    md_path.write_text(handoff.render_markdown())
    (run_dir / f"{slug}.json").write_text(handoff.model_dump_json(indent=2))
    current_handoff_path.parent.mkdir(parents=True, exist_ok=True)
    current_handoff_path.write_text(handoff.render_markdown())
    return md_path
