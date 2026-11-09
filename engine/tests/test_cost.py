"""Cost estimation, budget tracking, and gate decisions (P0 #4)."""

import json
from pathlib import Path

import pytest

from agentcrew.cost import (
    BudgetStatus,
    MODEL_RATES,
    RoleEstimate,
    RunEstimate,
    _rates_for,
    actual_cost_from_usage,
    decide_cost_gate,
    estimate_run,
    load_daily_so_far,
    record_run_cost,
)
from agentcrew.routing import Routing


# --- Model rates --------------------------------------------------------------


def test_known_model_rates_present():
    assert "claude-opus-4-7" in MODEL_RATES
    assert "claude-sonnet-4-6" in MODEL_RATES
    assert "gpt-4o" in MODEL_RATES


def test_explicit_local_model_is_free():
    assert _rates_for("local") == (0.0, 0.0)


def test_mock_models_are_free():
    assert _rates_for("mock-developer") == (0.0, 0.0)
    assert _rates_for("mock") == (0.0, 0.0)


@pytest.mark.parametrize("model", [
    "brand-new-model-not-in-table", "provider:model", "provider:gpt-4o",
    "qwen2.5-coder:32b", "llama3.3:70b",
])
def test_unknown_model_rates_are_unavailable(model):
    assert _rates_for(model) is None


# --- Role estimate ------------------------------------------------------------


def test_role_estimate_zero_for_local_model():
    est = RoleEstimate.compute(
        role="Developer",
        model="local",
        system_prompt_chars=5000,
        prior_handoff_count=2,
        gate_section_chars=2000,
        max_output_tokens=8192,
    )
    assert est.total_usd == 0.0
    # Tokens are still computed (for observability)
    assert est.input_tokens > 0
    assert est.output_tokens > 0


def test_role_estimate_scales_with_prior_handoffs():
    base = RoleEstimate.compute(
        role="Reviewer", model="claude-opus-4-7",
        system_prompt_chars=2000, prior_handoff_count=0,
        gate_section_chars=0, max_output_tokens=8192,
    )
    later = RoleEstimate.compute(
        role="Reviewer", model="claude-opus-4-7",
        system_prompt_chars=2000, prior_handoff_count=5,
        gate_section_chars=0, max_output_tokens=8192,
    )
    assert later.input_tokens > base.input_tokens
    assert later.total_usd > base.total_usd


def test_opus_costs_more_than_sonnet():
    opus = RoleEstimate.compute(
        role="Reviewer", model="claude-opus-4-7",
        system_prompt_chars=2000, prior_handoff_count=0,
        gate_section_chars=0, max_output_tokens=8192,
    )
    sonnet = RoleEstimate.compute(
        role="Reviewer", model="claude-sonnet-4-6",
        system_prompt_chars=2000, prior_handoff_count=0,
        gate_section_chars=0, max_output_tokens=8192,
    )
    assert opus.total_usd > sonnet.total_usd


# --- Run estimate -------------------------------------------------------------


def _routing(specialists=None) -> Routing:
    return Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix", starting_role="Developer",
        workflow="Developer -> Tester -> Human", specialists=specialists or [],
    )


def _estimate_for_models(model_for_role):
    return estimate_run(
        routing=_routing(),
        acting_roles=list(model_for_role),
        model_for_role=model_for_role,
        role_file_chars={},
        gate_section_chars_for_role={},
        max_tokens_per_role={},
    )


@pytest.mark.parametrize("model, unknown", [
    ("gpt-4o", False), ("claude-sonnet-4-6", False),
    ("mock", False), ("mock-developer", False), ("local", False),
    ("brand-new-model", True), ("provider:model", True),
    ("provider:gpt-4o", True), ("qwen2.5-coder:32b", True),
])
def test_run_estimate_exposes_unknown_pricing(model, unknown):
    est = _estimate_for_models({"Developer": model})

    assert est.has_unknown_model is unknown
    assert est.to_dict() == {
        "per_role": [{
            "role": "Developer", "model": model,
            "input_tokens": est.per_role[0].input_tokens,
            "output_tokens": est.per_role[0].output_tokens,
            "total_usd": round(est.per_role[0].total_usd, 4),
        }],
        "total_usd": round(est.total_usd, 4),
        "has_unknown_model": unknown,
    }
    table = est.render_table()
    assert ("Unknown pricing" in table) is unknown
    if unknown:
        assert table.splitlines()[2].endswith("UNKNOWN")
        assert "KNOWN TOTAL" in table
        assert "explicit approval" in table.lower()
    else:
        assert "UNKNOWN" not in table


@pytest.mark.parametrize("models", [
    {"Developer": "gpt-4o", "Tester": "provider:model"},
    {"Developer": "provider:model", "Tester": "gpt-4o"},
])
def test_mixed_estimate_retains_known_cost_and_unknown_flag(models):
    est = _estimate_for_models(models)

    assert est.has_unknown_model is True
    assert est.total_usd > 0
    assert est.total_usd == sum(e.total_usd for e in est.per_role if e.model == "gpt-4o")


def test_run_estimate_sums_per_role():
    est = estimate_run(
        routing=_routing(),
        acting_roles=["Developer", "Tester"],
        model_for_role={"Developer": "claude-sonnet-4-6", "Tester": "claude-sonnet-4-6"},
        role_file_chars={"Developer": 2000, "Tester": 1500},
        gate_section_chars_for_role={"Developer": 0, "Tester": 0},
        max_tokens_per_role={"Developer": 8192, "Tester": 6144},
    )
    assert len(est.per_role) == 2
    assert est.total_usd == pytest.approx(
        est.per_role[0].total_usd + est.per_role[1].total_usd
    )


def test_run_estimate_flags_unknown_model_when_role_unset():
    est = estimate_run(
        routing=_routing(),
        acting_roles=["Developer"],
        model_for_role={},  # nothing set
        role_file_chars={"Developer": 2000},
        gate_section_chars_for_role={"Developer": 0},
        max_tokens_per_role={"Developer": 8192},
    )
    assert est.has_unknown_model is True


# --- Cost gate ----------------------------------------------------------------


def _budget(daily_so_far=0.0, cap=0.0) -> BudgetStatus:
    return BudgetStatus(daily_so_far_usd=daily_so_far, daily_cap_usd=cap, today="2026-05-28")


def _est_at(total_usd: float) -> RunEstimate:
    e = RunEstimate()
    e.total_usd = total_usd
    return e


def test_no_warn_no_block_under_thresholds():
    gate = decide_cost_gate(
        _est_at(0.10),
        _budget(),
        per_run_warn_usd=0.50,
        per_run_block_usd=5.0,
    )
    assert not gate.warn
    assert not gate.block


def test_warn_between_warn_and_block():
    gate = decide_cost_gate(
        _est_at(0.75),
        _budget(),
        per_run_warn_usd=0.50,
        per_run_block_usd=5.0,
    )
    assert gate.warn is True
    assert gate.block is False


def test_block_over_per_run_threshold():
    gate = decide_cost_gate(
        _est_at(6.0),
        _budget(),
        per_run_warn_usd=0.50,
        per_run_block_usd=5.0,
    )
    assert gate.block is True
    assert "5.00" in gate.reason


def test_block_when_daily_cap_would_be_exceeded():
    gate = decide_cost_gate(
        _est_at(1.0),
        _budget(daily_so_far=9.5, cap=10.0),
        per_run_warn_usd=0.50,
        per_run_block_usd=5.0,
    )
    assert gate.block is True
    assert "daily cap" in gate.reason.lower()


def test_zero_thresholds_disable_warn_and_block():
    """Zero thresholds disable numeric caps for fully priced estimates."""
    gate = decide_cost_gate(
        _est_at(100.0),
        _budget(),  # no daily cap either
        per_run_warn_usd=0,
        per_run_block_usd=0,
    )
    assert not gate.warn
    assert not gate.block


@pytest.mark.parametrize("model", ["new-hosted-model", "provider:model", "qwen2.5-coder:32b", ""])
@pytest.mark.parametrize("warn_usd, block_usd", [(0, 0), (0.5, 5.0)])
def test_unknown_pricing_requires_explicit_approval(model, warn_usd, block_usd):
    est = _estimate_for_models({"Developer": model})

    gate = decide_cost_gate(
        est, _budget(), per_run_warn_usd=warn_usd, per_run_block_usd=block_usd,
    )

    assert gate.block is True
    assert gate.warn is False
    assert "unknown" in gate.reason.lower()
    assert "explicit" in gate.reason.lower()
    assert "approval" in gate.reason.lower()


@pytest.mark.parametrize("model", ["gpt-4o", "mock", "mock-developer", "local"])
def test_known_pricing_does_not_require_unknown_cost_approval(model):
    gate = decide_cost_gate(
        _estimate_for_models({"Developer": model}), _budget(),
        per_run_warn_usd=0, per_run_block_usd=0,
    )

    assert (gate.block, gate.warn, gate.reason) == (False, False, "")


@pytest.mark.parametrize("cap, expected_reason", [(0, "per-run block"), (5, "daily cap")])
def test_unknown_pricing_does_not_hide_exceeded_caps(cap, expected_reason):
    est = RunEstimate(total_usd=6.0, has_unknown_model=True)

    gate = decide_cost_gate(
        est, _budget(cap=cap), per_run_warn_usd=0.5, per_run_block_usd=5,
    )

    assert gate.block is True
    assert expected_reason in gate.reason
    assert "unknown" in gate.reason.lower()
    assert "approval" in gate.reason.lower()


# --- Budget tracking on disk --------------------------------------------------


def test_record_and_load_daily_total(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()
    record_run_cost(project, run_id="r1", cost_usd=0.10)
    record_run_cost(project, run_id="r2", cost_usd=0.25)
    status = load_daily_so_far(project, daily_cap_usd=1.0)
    assert status.daily_so_far_usd == pytest.approx(0.35)
    assert status.remaining_usd == pytest.approx(0.65)


def test_load_daily_so_far_when_no_log(tmp_path):
    status = load_daily_so_far(tmp_path / "proj", daily_cap_usd=5.0)
    assert status.daily_so_far_usd == 0.0
    assert status.remaining_usd == 5.0


def test_remaining_is_infinite_when_no_cap(tmp_path):
    status = load_daily_so_far(tmp_path / "proj", daily_cap_usd=0.0)
    assert status.remaining_usd == float("inf")


def test_malformed_log_lines_do_not_discard_known_subtotal(tmp_path):
    project = tmp_path / "proj"
    (project / ".agent-state").mkdir(parents=True)
    log = project / ".agent-state" / "budget-history.jsonl"
    log.write_text(
        '{"date": "2026-05-28", "cost_usd": 0.1}\n'
        'this is not json\n'
        '{"date": "2026-05-28", "cost_usd": "not a number"}\n'
        '{"date": "2026-05-28", "cost_usd": 0.2}\n'
    )
    # Patch _today_iso to match the fixture data
    import agentcrew.cost as cost_mod
    real = cost_mod._today_iso
    cost_mod._today_iso = lambda: "2026-05-28"
    try:
        status = load_daily_so_far(project, daily_cap_usd=1.0)
        assert status.daily_so_far_usd == pytest.approx(0.3)
        assert status.has_unresolved_spend is True
    finally:
        cost_mod._today_iso = real


# --- Actual cost from provider usage ------------------------------------------


def test_actual_cost_from_usage_known_model():
    cost = actual_cost_from_usage(
        "claude-sonnet-4-6",
        {"input_tokens": 1000, "output_tokens": 500},
    )
    # 1000 * 3 / 1M + 500 * 15 / 1M = 0.003 + 0.0075 = 0.0105
    assert cost == pytest.approx(0.0105)


def test_actual_cost_from_usage_unknown_model_is_unresolved():
    cost = actual_cost_from_usage(
        "qwen2.5-coder:7b",
        {"input_tokens": 100_000, "output_tokens": 50_000},
    )
    assert cost is None


def test_actual_cost_handles_missing_usage():
    assert actual_cost_from_usage("claude-opus-4-7", {}) == 0.0
    assert actual_cost_from_usage("claude-opus-4-7", {"input_tokens": None}) == 0.0


@pytest.mark.parametrize("usage", [
    {"input_tokens": 1000, "output_tokens": 500},
    {"prompt_tokens": 1000, "completion_tokens": 500},
    {"input_tokens": "1000", "completion_tokens": "500"},
    {"input_tokens": 1000, "output_tokens": 500, "prompt_tokens": 9000, "completion_tokens": 9000},
])
def test_actual_cost_accepts_normalized_and_legacy_openai_usage(usage):
    assert actual_cost_from_usage("gpt-4o", usage) == pytest.approx(0.0075)


def test_actual_cost_prefers_explicit_normalized_zero():
    usage = {"input_tokens": 0, "output_tokens": 0, "prompt_tokens": 1000, "completion_tokens": 500}
    assert actual_cost_from_usage("gpt-4o", usage) == 0.0


def test_actual_cost_does_not_double_count_openai_cached_input():
    usage = {"input_tokens": 1000, "output_tokens": 500, "cache_read_input_tokens": 800}
    assert actual_cost_from_usage("gpt-4o", usage) is None


# --- End-to-end orchestrator integration --------------------------------------


def test_orchestrator_writes_cost_estimate_and_actual(tmp_path):
    from agentcrew.demo_script import demo_provider
    from agentcrew.orchestrator import auto_approve, run as run_team
    from agentcrew.agentcrew_root import find_agentcrew_root

    project = tmp_path / "proj"
    project.mkdir()
    (project / "broken.py").write_text("def add_numbers(a, b): return a - b\n")
    (project / "test_broken.py").write_text(
        "import unittest\n"
        "from broken import add_numbers\n\n"
        "class AddNumbersTest(unittest.TestCase):\n"
        "    def test_adds(self):\n"
        "        self.assertEqual(add_numbers(2, 3), 5)\n"
    )

    root = find_agentcrew_root()
    result = run_team(
        task="Fix broken.py so add_numbers returns a + b",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role={r: f"mock-{r}" for r in (
            "Developer", "Tester", "Reviewer",
            "Security Reviewer", "UX / Design Reviewer",
        )},
        routing_approver=auto_approve,
    )
    # cost-estimate.json exists, even for mock providers (cost is $0 there)
    estimate_path = result.run_dir / "cost-estimate.json"
    actual_path = result.run_dir / "cost-actual.json"
    assert estimate_path.exists()
    assert actual_path.exists()

    estimate = json.loads(estimate_path.read_text())
    assert "per_role" in estimate["estimate"]
    assert estimate["estimate"]["total_usd"] == 0.0  # mock models
    actual = json.loads(actual_path.read_text())
    assert actual["actual_cost_usd"] == 0.0


def test_orchestrator_blocks_when_estimate_exceeds_block_threshold(tmp_path):
    """A config with a tiny per_run_block_usd should stop the run cold."""
    from agentcrew.demo_script import demo_provider
    from agentcrew.orchestrator import run as run_team
    from agentcrew.agentcrew_root import find_agentcrew_root

    project = tmp_path / "proj"
    project.mkdir()
    (project / "broken.py").write_text("def add_numbers(a, b): return a - b\n")
    (project / ".agentcrew").mkdir()
    (project / ".agentcrew" / "config.yaml").write_text(
        "budget:\n"
        "  per_run_block_usd: 0.0001\n"  # tiny
    )

    root = find_agentcrew_root()
    # Use real model names so cost > 0
    rejections = []
    def reject(_gate):
        rejections.append(_gate.reason)
        return False

    result = run_team(
        task="Refactor the auth middleware to support OIDC",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role={r: "claude-opus-4-7" for r in (
            "Advisor", "Idea Consultant", "Product Manager",
            "Developer", "Tester", "Reviewer",
            "Security Reviewer", "UX / Design Reviewer",
        )},
        cost_approver=reject,
    )
    assert result.final_decision == "cost_rejected_by_human"
    assert result.next_owner == "human"
    assert rejections, "cost_approver should have been called"
    assert "exceeds" in rejections[0].lower() or "cap" in rejections[0].lower()
    # No handoffs were produced — nothing actually ran.
    assert result.handoffs == []
