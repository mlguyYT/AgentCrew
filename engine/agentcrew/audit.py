"""`agentcrew audit` — cross-run aggregation for VP-of-Eng visibility.

Walks .agent-state/runs/ and summarizes:
  - total runs in the date range
  - breakdown by lane (Fast/Full/Direct Answer)
  - breakdown by recipe (bug-fix/feature/refactor/release/...)
  - breakdown by final_decision (approval/blocked/rework)
  - specialists invoked (Security Reviewer, UX, ...)
  - gates triggered
  - cost: total spend, average per run, top 5 most expensive runs
  - rate of human-blocked runs (where human approval is the next owner)

No LLM call; pure file aggregation.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class AuditEntry:
    run_id: str
    run_dir: Path
    date: str
    task: str
    lane: str
    recipe: str
    risk: str
    profile: str
    workflow: str
    specialists: list[str]
    gates: list[str]
    final_decision: str
    next_owner: str
    estimated_cost: float
    actual_cost: float

    @property
    def is_blocked(self) -> bool:
        return self.final_decision.startswith(("blocked", "rejected", "hold_", "cost_", "mid_workflow"))


@dataclass
class AuditReport:
    entries: list[AuditEntry] = field(default_factory=list)
    since: str = ""
    until: str = ""

    @property
    def total_runs(self) -> int:
        return len(self.entries)

    def by_lane(self) -> Counter:
        return Counter(e.lane for e in self.entries if e.lane)

    def by_recipe(self) -> Counter:
        return Counter(e.recipe for e in self.entries if e.recipe)

    def by_final_decision(self) -> Counter:
        return Counter(e.final_decision for e in self.entries if e.final_decision)

    def specialists_invoked(self) -> Counter:
        c: Counter = Counter()
        for e in self.entries:
            for s in e.specialists:
                c[s] += 1
        return c

    def gates_triggered(self) -> Counter:
        c: Counter = Counter()
        for e in self.entries:
            for g in e.gates:
                c[g] += 1
        return c

    @property
    def total_actual_cost(self) -> float:
        return sum(e.actual_cost for e in self.entries)

    @property
    def total_estimated_cost(self) -> float:
        return sum(e.estimated_cost for e in self.entries)

    @property
    def avg_actual_per_run(self) -> float:
        return self.total_actual_cost / self.total_runs if self.total_runs else 0.0

    def top_n_expensive(self, n: int = 5) -> list[AuditEntry]:
        return sorted(self.entries, key=lambda e: e.actual_cost, reverse=True)[:n]

    @property
    def blocked_rate(self) -> float:
        if not self.entries:
            return 0.0
        return sum(1 for e in self.entries if e.is_blocked) / self.total_runs


def _read_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}


def _parse_entry(run_dir: Path) -> AuditEntry | None:
    routing = _read_json(run_dir / "task-routing.json")
    if not routing:
        return None
    cost_est = _read_json(run_dir / "cost-estimate.json")
    cost_act = _read_json(run_dir / "cost-actual.json")
    summary = (run_dir / "summary.md").read_text() if (run_dir / "summary.md").exists() else ""
    task = ""
    task_md = run_dir / "task.md"
    if task_md.exists():
        task = task_md.read_text().replace("# Task\n\n", "").strip()

    final_decision = ""
    next_owner = ""
    for line in summary.splitlines():
        line = line.strip()
        if line.startswith("Final decision:"):
            final_decision = line.split(":", 1)[1].strip()
        elif line.startswith("Next owner:"):
            next_owner = line.split(":", 1)[1].strip()

    # Run id format starts with YYYYMMDD; derive date from that.
    date_str = ""
    rid = run_dir.name
    if len(rid) >= 8 and rid[:8].isdigit():
        date_str = f"{rid[:4]}-{rid[4:6]}-{rid[6:8]}"

    return AuditEntry(
        run_id=run_dir.name,
        run_dir=run_dir,
        date=date_str,
        task=task[:120],
        lane=routing.get("lane", ""),
        recipe=routing.get("recipe", ""),
        risk=routing.get("risk", ""),
        profile=routing.get("quality_profile", ""),
        workflow=routing.get("workflow", ""),
        specialists=routing.get("specialists") or [],
        gates=routing.get("gates") or [],
        final_decision=final_decision,
        next_owner=next_owner,
        estimated_cost=float((cost_est.get("estimate") or {}).get("total_usd", 0) or 0),
        actual_cost=float(cost_act.get("actual_cost_usd", 0) or 0),
    )


def collect(
    project_dir: Path,
    *,
    since: str | None = None,
    until: str | None = None,
) -> AuditReport:
    """Walk .agent-state/runs/ and build a report.

    `since` / `until` are ISO dates (YYYY-MM-DD). Entries outside the range
    are skipped. Either bound may be omitted.
    """
    report = AuditReport(since=since or "", until=until or "")
    runs_dir = project_dir / ".agent-state" / "runs"
    if not runs_dir.exists():
        return report
    for d in sorted(runs_dir.iterdir()):
        if not d.is_dir():
            continue
        entry = _parse_entry(d)
        if entry is None:
            continue
        if since and entry.date and entry.date < since:
            continue
        if until and entry.date and entry.date > until:
            continue
        report.entries.append(entry)
    return report


def render(report: AuditReport) -> str:
    if report.total_runs == 0:
        return "No runs to audit."

    range_txt = ""
    if report.since or report.until:
        range_txt = f" ({report.since or '...'} → {report.until or '...'})"

    out = []
    out.append("=" * 72)
    out.append(f"AgentCrew audit{range_txt}")
    out.append("=" * 72)
    out.append(f"Total runs:    {report.total_runs}")
    out.append(f"Blocked rate:  {report.blocked_rate*100:.1f}%")
    out.append("")

    out.append("By lane:")
    for lane, count in report.by_lane().most_common():
        out.append(f"  {count:>4}  {lane}")
    out.append("")

    out.append("By recipe:")
    for recipe, count in report.by_recipe().most_common():
        out.append(f"  {count:>4}  {recipe}")
    out.append("")

    specs = report.specialists_invoked()
    if specs:
        out.append("Specialists invoked:")
        for role, count in specs.most_common():
            out.append(f"  {count:>4}  {role}")
        out.append("")

    gates = report.gates_triggered()
    if gates:
        out.append("Gates triggered:")
        for gate, count in gates.most_common(10):
            out.append(f"  {count:>4}  {gate}")
        out.append("")

    final = report.by_final_decision()
    if final:
        out.append("Final decisions:")
        for dec, count in final.most_common(10):
            out.append(f"  {count:>4}  {dec}")
        out.append("")

    out.append(f"Cost:")
    out.append(f"  Total estimated: ${report.total_estimated_cost:.4f}")
    out.append(f"  Total actual:    ${report.total_actual_cost:.4f}")
    out.append(f"  Avg per run:     ${report.avg_actual_per_run:.4f}")

    top = [e for e in report.top_n_expensive(5) if e.actual_cost > 0]
    if top:
        out.append("")
        out.append("Most expensive runs:")
        for e in top:
            out.append(f"  ${e.actual_cost:.4f}  {e.run_id}  {e.task[:80]}")

    return "\n".join(out)
