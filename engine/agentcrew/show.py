"""`agentcrew show` — render the latest run as a single-screen summary.

Reads .agent-state/runs/<latest>/ and prints:
  - Task, routing (lane/risk/recipe/profile)
  - Workflow + handoffs (sender → receiver: decision)
  - Cost (estimate vs actual, daily total)
  - Open questions and human decisions
  - Path to the run dir

No LLM call; pure file I/O.
"""

from __future__ import annotations

import json
from pathlib import Path


def find_latest_run(project_dir: Path) -> Path | None:
    runs = project_dir / ".agent-state" / "runs"
    if not runs.exists():
        return None
    candidates = sorted([p for p in runs.iterdir() if p.is_dir()], reverse=True)
    return candidates[0] if candidates else None


def _read_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def render_run(run_dir: Path) -> str:
    """Format one run dir as a tight one-screen summary."""
    summary_md = _read_text(run_dir / "summary.md")
    routing_json = _read_json(run_dir / "task-routing.json")
    cost_est = _read_json(run_dir / "cost-estimate.json")
    cost_act = _read_json(run_dir / "cost-actual.json")
    task = _read_text(run_dir / "task.md").replace("# Task\n\n", "").strip()
    plan = _read_json(run_dir / "plan.json")

    out = []
    out.append("=" * 72)
    out.append(f"Run: {run_dir.name}")
    out.append("=" * 72)
    if task:
        out.append(f"Task:    {task[:200]}")
    if routing_json:
        out.append(
            f"Routing: {routing_json.get('lane', '?')}  ·  "
            f"recipe={routing_json.get('recipe', '?')}  ·  "
            f"profile={routing_json.get('quality_profile', '?')}  ·  "
            f"risk={routing_json.get('risk', '?')}"
        )
        wf = routing_json.get("workflow", "")
        if wf:
            out.append(f"Workflow: {wf}")
        specs = routing_json.get("specialists") or []
        if specs:
            out.append(f"Specialists: {', '.join(specs)}")
        gates = routing_json.get("gates") or []
        if gates:
            out.append(f"Gates: {', '.join(gates)}")

    # Handoffs — read each <sender>-to-<receiver>.json (or *.json under runs)
    handoff_files = sorted(
        [p for p in run_dir.glob("*.json") if "-to-" in p.stem],
        key=lambda p: p.stat().st_mtime,
    )
    if handoff_files:
        out.append("")
        out.append("Handoffs:")
        for hf in handoff_files:
            data = _read_json(hf)
            sender = data.get("sender", "?")
            receiver = data.get("receiver", "?")
            decision = data.get("decision", "?")
            out.append(f"  - {sender} → {receiver}: {decision}")

    # Cost
    if cost_est or cost_act:
        out.append("")
        out.append("Cost:")
        est_total = (cost_est.get("estimate") or {}).get("total_usd", 0)
        actual_total = cost_act.get("actual_cost_usd", 0)
        daily_after = cost_act.get("daily_total_after", 0)
        out.append(f"  estimated: ${est_total:.4f}")
        out.append(f"  actual:    ${actual_total:.4f}")
        if cost_est.get("daily_cap_usd"):
            out.append(
                f"  daily:     ${daily_after:.4f} of ${cost_est['daily_cap_usd']:.2f} cap"
            )

    # Plan if present (Planner runs)
    if plan and plan.get("summary"):
        out.append("")
        out.append(f"Plan: {plan['summary']}")

    # Final decision from summary
    for line in summary_md.splitlines():
        line = line.strip()
        if line.startswith("Final decision:") or line.startswith("Next owner:"):
            out.append(line)

    out.append("")
    out.append(f"Artifacts: {run_dir}")
    return "\n".join(out)


def render_latest(project_dir: Path) -> str:
    """Find and render the latest run for a project."""
    latest = find_latest_run(project_dir)
    if latest is None:
        return f"No runs found in {project_dir / '.agent-state' / 'runs'}/"
    return render_run(latest)
