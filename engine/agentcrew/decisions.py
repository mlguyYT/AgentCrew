"""Team decision continuity — `.agent-state/decisions.md`.

A persistent, append-only log of decisions the team has made. Read into
every role's context so:

  - The Reviewer doesn't re-relitigate a choice the team already made
  - The Developer follows established conventions ("we use Postgres for X")
  - The Security Reviewer can verify decisions against current behavior

Format (Markdown, one entry per decision):

    ## 2026-05-28 · Use Postgres for the dashboard backing store
    Decided by: Product Manager, Reviewer
    Run: 20260528-123045-abc123
    Rationale: Existing infra; Reviewer flagged SQLite as a scaling risk.

The orchestrator appends to this file when a role's handoff includes
decision-shaped evidence. The CLI exposes `agentcrew decisions add` for
the human to record agreements.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


# Header used for parsing existing entries
_ENTRY_RX = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s+·\s+(.+)$", re.MULTILINE)


def _ensure_file(decisions_path: Path) -> None:
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    if not decisions_path.exists():
        decisions_path.write_text(
            "# Team Decisions\n\n"
            "Append-only record of agreements the team has made. Read by every role\n"
            "before it acts. Do not delete entries; supersede them with a new one.\n\n"
        )


def record_decision(
    decisions_path: Path,
    *,
    title: str,
    decided_by: list[str],
    rationale: str,
    run_id: str | None = None,
) -> None:
    """Append a new decision entry."""
    _ensure_file(decisions_path)
    date = datetime.now(timezone.utc).date().isoformat()
    parts = [f"## {date} · {title.strip()}"]
    if decided_by:
        parts.append(f"Decided by: {', '.join(decided_by)}")
    if run_id:
        parts.append(f"Run: {run_id}")
    if rationale:
        parts.append(f"Rationale: {rationale.strip()}")
    parts.append("")
    with decisions_path.open("a") as f:
        f.write("\n" + "\n".join(parts) + "\n")


def load_recent(decisions_path: Path, *, limit: int = 10) -> str:
    """Return the most recent `limit` decisions as Markdown.

    Returned text is safe to inject into a role's user message — it omits
    the file header and renders only the entries themselves.
    """
    if not decisions_path.exists():
        return ""
    text = decisions_path.read_text()
    # Find every "## YYYY-MM-DD · ..." header position
    matches = list(_ENTRY_RX.finditer(text))
    if not matches:
        return ""
    # Slice the most recent N (file is append-only so last = newest)
    selected = matches[-limit:]
    starts = [m.start() for m in selected]
    starts.append(len(text))
    blocks = []
    for i, start in enumerate(starts[:-1]):
        blocks.append(text[start:starts[i + 1]].rstrip())
    return "\n\n".join(blocks)


def render_section(decisions_text: str) -> str:
    """Wrap decisions in a labeled section for the user-message context."""
    if not decisions_text.strip():
        return ""
    return (
        "## Team decisions (from .agent-state/decisions.md)\n\n"
        "The team has previously agreed to these. Do not re-debate them; "
        "follow them unless the task explicitly overrides one.\n\n"
        f"{decisions_text}\n"
    )
