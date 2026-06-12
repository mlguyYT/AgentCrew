"""Opt-in anonymous telemetry."""

import json
from pathlib import Path

from agentcrew.telemetry import (
    _classify_decision,
    _family_for_model,
    emit_run_event,
    read_recent,
)


# --- Model family bucketing ---


def test_family_for_claude_models():
    assert _family_for_model("claude-opus-4-7") == "claude-opus"
    assert _family_for_model("claude-sonnet-4-6") == "claude-sonnet"
    assert _family_for_model("claude-haiku-4-5") == "claude-haiku"


def test_family_for_openai_models():
    assert _family_for_model("gpt-4o") == "gpt-4"
    assert _family_for_model("gpt-4o-mini") == "gpt-4o-mini"
    assert _family_for_model("gpt-4.1") == "gpt-4"
    assert _family_for_model("o1-mini") == "o1"


def test_family_for_local_models():
    assert _family_for_model("qwen2.5-coder:32b") == "local"
    assert _family_for_model("llama3.3:70b") == "local"


def test_family_for_mock():
    assert _family_for_model("mock-developer") == "mock"
    assert _family_for_model("mock") == "mock"


def test_family_for_unset_or_other():
    assert _family_for_model("") == "unset"
    assert _family_for_model("brand-new-thing") == "other"


# --- Decision bucketing ---


def test_decision_bucketing():
    assert _classify_decision("ready_for_human_approval") == "approved"
    assert _classify_decision("ready_for_human_release_review") == "approved"
    assert _classify_decision("needs_rework") == "rework"
    assert _classify_decision("blocked_open_question") == "blocked"
    assert _classify_decision("rejected_scope") == "rejected"
    assert _classify_decision("cost_rejected_by_human") == "cost_gate"
    assert _classify_decision("protocol_failure") == "infra_failure"
    assert _classify_decision("answered") == "direct_answer"
    assert _classify_decision("something else") == "other"
    assert _classify_decision("") == "unknown"


# --- Disabled = no-op ---


def test_emit_disabled_is_noop(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    emit_run_event(
        p, enabled=False,
        run_id="r1", lane="Fast Lane", recipe="bug-fix", risk="low",
        quality_profile="standard",
        acting_roles_count=2, specialists_count=0, gates_count=1,
        final_decision="ready_for_human_approval", next_owner="human",
        estimated_cost_usd=0.0, actual_cost_usd=0.0,
        duration_seconds=1.0, models_by_role={"Developer": "mock"},
    )
    assert not (p / ".agent-state" / "telemetry.jsonl").exists()


# --- Enabled writes a record ---


def test_emit_enabled_writes_record(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    emit_run_event(
        p, enabled=True,
        run_id="20260528-100000-abc",
        lane="Full Lane", recipe="feature", risk="high",
        quality_profile="strict",
        acting_roles_count=4, specialists_count=1, gates_count=3,
        final_decision="ready_for_human_approval", next_owner="human",
        estimated_cost_usd=0.42, actual_cost_usd=0.38,
        duration_seconds=12.5,
        models_by_role={"Developer": "claude-sonnet-4-6", "Reviewer": "claude-opus-4-7"},
    )
    log = p / ".agent-state" / "telemetry.jsonl"
    assert log.exists()
    rec = json.loads(log.read_text().strip())
    # Anonymization checks
    assert "lane" in rec
    assert rec["lane"] == "Full Lane"
    assert rec["final_class"] == "approved"
    assert sorted(rec["model_families"]) == ["claude-opus", "claude-sonnet"]
    # No task text, no file paths
    assert "task" not in rec
    assert "/" not in json.dumps(rec)
    # Run id is hashed, not raw
    assert rec["run_id_hash"] != "20260528-100000-abc"
    assert len(rec["run_id_hash"]) == 12


def test_read_recent_returns_last_n(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    for i in range(7):
        emit_run_event(
            p, enabled=True, run_id=f"r{i}",
            lane="Fast Lane", recipe="bug-fix", risk="low",
            quality_profile="standard",
            acting_roles_count=2, specialists_count=0, gates_count=0,
            final_decision="ready_for_human_approval", next_owner="human",
            estimated_cost_usd=0.0, actual_cost_usd=0.0,
            duration_seconds=1.0, models_by_role={},
        )
    recs = read_recent(p, limit=3)
    assert len(recs) == 3
