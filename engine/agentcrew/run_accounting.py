"""Finalize received usage independently of handoff validity or workflow type."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from .cost import CostSummary, cost_summary, load_daily_so_far, record_run_cost
from .state_paths import checked_state_path

if TYPE_CHECKING:
    from .orchestrator import TeamRun


def finalize_accounting(state: TeamRun, *, run_dir: Path | None = None, daily_cap: float = 0.0) -> None:
    """Persist known spending and uncertainty, even after invalid model output.

    Free advisory calls with no usage need no project artifacts. Paid advisory
    calls write only the budget ledger; workflow calls also write a cost report.
    """

    known_total = 0.0
    pricing_known = True
    unresolved = []
    for agent_run in state.agent_runs:
        try:
            summary = cost_summary(agent_run.model, agent_run.usage, agent_run.provider)
        except (TypeError, ValueError, AttributeError, OverflowError):
            summary = CostSummary(0.0, False, {})
        known_total += summary.known_cost_usd
        complete = (agent_run.provider in {"mock", "local"}
                    or not agent_run.stop_reason.startswith("provider_error:"))
        if agent_run.provider not in {"", "mock", "local"} and not agent_run.usage:
            complete = False
        pricing_known &= summary.pricing_known and complete
        if not summary.pricing_known or not complete:
            unresolved.append({
                "model": agent_run.model,
                "provider": agent_run.provider,
                "usage": summary.unresolved_usage,
                "usage_complete": complete,
            })
    state.actual_cost_usd = known_total
    state.pricing_known = pricing_known
    state.unresolved_usage = unresolved
    if known_total > 0 or not pricing_known:
        record_run_cost(state.project_dir, run_id=state.run_id, cost_usd=known_total,
                        pricing_known=pricing_known, unresolved_usage=unresolved)
    if run_dir is not None:
        budget = load_daily_so_far(state.project_dir, daily_cap_usd=daily_cap)
        report = checked_state_path(run_dir, run_dir / "cost-actual.json")
        report.write_text(json.dumps({
            "actual_cost_usd": round(known_total, 6) if pricing_known else None,
            "known_cost_usd": round(known_total, 6),
            "pricing_known": pricing_known,
            "unresolved_usage": unresolved,
            "estimated_cost_usd": round(state.cost_estimate.total_usd, 6) if state.cost_estimate else 0.0,
            "daily_total_after": round(budget.daily_so_far_usd, 6),
            "daily_pricing_known": not budget.has_unresolved_spend,
        }, indent=2))
