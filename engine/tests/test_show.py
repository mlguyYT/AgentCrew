"""`agentcrew show` last-run renderer."""

import json
from pathlib import Path

from agentcrew.show import find_latest_run, render_latest, render_run


def _make_run(project: Path, run_id: str) -> Path:
    run_dir = project / ".agent-state" / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "task.md").write_text("# Task\n\nFix the auth flow\n")
    (run_dir / "task-routing.json").write_text(json.dumps({
        "lane": "Full Lane",
        "recipe": "feature",
        "quality_profile": "strict",
        "risk": "high",
        "workflow": "Developer -> Tester -> Reviewer -> Security Reviewer -> Human",
        "specialists": ["Security Reviewer"],
        "gates": ["dependency and supply-chain gate"],
    }))
    (run_dir / "developer-to-tester.json").write_text(json.dumps({
        "sender": "Developer", "receiver": "Tester", "decision": "ready_for_test",
    }))
    (run_dir / "tester-to-reviewer.json").write_text(json.dumps({
        "sender": "Tester", "receiver": "Reviewer", "decision": "ready_for_review",
    }))
    (run_dir / "cost-estimate.json").write_text(json.dumps({
        "estimate": {"total_usd": 0.42, "per_role": []},
        "daily_cap_usd": 5.0,
    }))
    (run_dir / "cost-actual.json").write_text(json.dumps({
        "actual_cost_usd": 0.38,
        "daily_total_after": 1.21,
    }))
    (run_dir / "summary.md").write_text(
        "# Run x\nTask: foo\nFinal decision: ready_for_human_approval\nNext owner: human\n"
    )
    return run_dir


def test_find_latest_picks_most_recent_id(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "20260528-100000-aaaaaa")
    _make_run(p, "20260528-200000-bbbbbb")
    _make_run(p, "20260528-150000-cccccc")
    latest = find_latest_run(p)
    assert latest.name == "20260528-200000-bbbbbb"


def test_no_runs_returns_friendly_message(tmp_path):
    out = render_latest(tmp_path / "proj")
    assert "No runs found" in out


def test_render_includes_routing_handoffs_cost(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "20260528-200000-bbbbbb")
    out = render_latest(p)
    # Routing
    assert "Full Lane" in out
    assert "feature" in out
    assert "strict" in out
    # Workflow + specialists + gates
    assert "Specialists: Security Reviewer" in out
    assert "dependency and supply-chain gate" in out
    # Handoffs
    assert "Developer → Tester: ready_for_test" in out
    assert "Tester → Reviewer: ready_for_review" in out
    # Cost
    assert "$0.4200" in out  # estimate
    assert "$0.3800" in out  # actual
    assert "$1.2100" in out and "$5.00" in out  # daily / cap
    # Final state
    assert "Final decision: ready_for_human_approval" in out


def test_render_specific_run_by_id(tmp_path):
    p = tmp_path / "proj"
    older = _make_run(p, "20260528-100000-aaaaaa")
    _make_run(p, "20260528-200000-bbbbbb")
    out = render_run(older)
    assert "20260528-100000-aaaaaa" in out
