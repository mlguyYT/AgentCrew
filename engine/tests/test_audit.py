"""Cross-run audit aggregation."""

import json
from pathlib import Path

from agentcrew.audit import AuditReport, collect, render


def _make_run(
    project: Path,
    run_id: str,
    *,
    lane="Fast Lane", recipe="bug-fix", risk="low", profile="standard",
    specialists=None, gates=None,
    final_decision="ready_for_human_approval",
    actual_cost=0.10, estimated_cost=0.12,
) -> Path:
    run_dir = project / ".agent-state" / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "task.md").write_text("# Task\n\nDo a thing\n")
    (run_dir / "task-routing.json").write_text(json.dumps({
        "lane": lane, "recipe": recipe, "risk": risk, "quality_profile": profile,
        "workflow": "Developer -> Tester -> Human",
        "specialists": specialists or [],
        "gates": gates or [],
    }))
    (run_dir / "cost-estimate.json").write_text(json.dumps({
        "estimate": {"total_usd": estimated_cost, "per_role": []},
        "daily_cap_usd": 5.0,
    }))
    (run_dir / "cost-actual.json").write_text(json.dumps({
        "actual_cost_usd": actual_cost,
        "daily_total_after": actual_cost,
    }))
    (run_dir / "summary.md").write_text(
        f"# Run\nFinal decision: {final_decision}\nNext owner: human\n"
    )
    return run_dir


def test_no_runs_is_empty_report(tmp_path):
    report = collect(tmp_path / "proj")
    assert report.total_runs == 0
    assert "No runs to audit" in render(report)


def test_counts_runs(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "20260528-100000-a")
    _make_run(p, "20260528-200000-b", lane="Full Lane", recipe="feature")
    _make_run(p, "20260529-100000-c")
    report = collect(p)
    assert report.total_runs == 3


def test_by_lane_and_recipe(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "r1", lane="Fast Lane", recipe="bug-fix")
    _make_run(p, "r2", lane="Fast Lane", recipe="bug-fix")
    _make_run(p, "r3", lane="Full Lane", recipe="feature")
    report = collect(p)
    assert report.by_lane()["Fast Lane"] == 2
    assert report.by_lane()["Full Lane"] == 1
    assert report.by_recipe()["bug-fix"] == 2
    assert report.by_recipe()["feature"] == 1


def test_specialists_and_gates_counted(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "r1", specialists=["Security Reviewer"], gates=["tester validation"])
    _make_run(p, "r2", specialists=["Security Reviewer", "UX / Design Reviewer"],
              gates=["tester validation", "dependency and supply-chain gate"])
    report = collect(p)
    assert report.specialists_invoked()["Security Reviewer"] == 2
    assert report.specialists_invoked()["UX / Design Reviewer"] == 1
    assert report.gates_triggered()["tester validation"] == 2
    assert report.gates_triggered()["dependency and supply-chain gate"] == 1


def test_cost_aggregation(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "r1", actual_cost=0.10, estimated_cost=0.12)
    _make_run(p, "r2", actual_cost=0.30, estimated_cost=0.25)
    _make_run(p, "r3", actual_cost=0.05, estimated_cost=0.08)
    report = collect(p)
    assert abs(report.total_actual_cost - 0.45) < 1e-6
    assert abs(report.total_estimated_cost - 0.45) < 1e-6
    assert abs(report.avg_actual_per_run - 0.15) < 1e-6


def test_top_expensive(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "r1", actual_cost=0.10)
    _make_run(p, "r2", actual_cost=0.50)
    _make_run(p, "r3", actual_cost=0.30)
    report = collect(p)
    top = report.top_n_expensive(2)
    assert [e.run_id for e in top] == ["r2", "r3"]


def test_blocked_rate(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "r1", final_decision="ready_for_human_approval")
    _make_run(p, "r2", final_decision="blocked_open_question")
    _make_run(p, "r3", final_decision="cost_rejected_by_human")
    _make_run(p, "r4", final_decision="rejected_scope")
    report = collect(p)
    assert report.blocked_rate == 0.75


def test_date_range_filter(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "20260527-100000-a")
    _make_run(p, "20260528-100000-b")
    _make_run(p, "20260529-100000-c")
    report = collect(p, since="2026-05-28", until="2026-05-28")
    assert [e.run_id for e in report.entries] == ["20260528-100000-b"]


def test_render_smoke(tmp_path):
    p = tmp_path / "proj"
    _make_run(p, "r1", specialists=["Security Reviewer"], gates=["tester validation"])
    _make_run(p, "r2", lane="Full Lane", recipe="feature", actual_cost=0.50)
    txt = render(collect(p))
    assert "AgentCrew audit" in txt
    assert "Total runs:    2" in txt
    assert "Fast Lane" in txt
    assert "Full Lane" in txt
    assert "Security Reviewer" in txt
    assert "Most expensive runs:" in txt
