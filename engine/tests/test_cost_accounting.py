"""Unpriced provider usage must remain visible across daily budget checks."""

import json
import os

import pytest

from agentcrew.cost import (
    BudgetStatus, CostSummary, RunEstimate, actual_cost_from_usage, cost_summary,
    decide_cost_gate, load_daily_so_far, record_run_cost,
)
from agentcrew.state_paths import UnsafeStatePath


@pytest.mark.parametrize("provider", ["", "openai"])
def test_fully_priced_usage_preserves_numeric_compatibility(provider):
    usage = {"input_tokens": 1000, "output_tokens": 500}
    assert cost_summary("gpt-4o", usage, provider) == CostSummary(0.0075, True)
    assert actual_cost_from_usage("gpt-4o", usage, provider) == 0.0075


@pytest.mark.parametrize("model,provider", [
    ("new-model", "openai"), ("gpt-4o", "gateway"),
    ("claude-sonnet-4-6", "openai"), ("gpt-4o", "anthropic"),
])
def test_missing_billing_rates_are_not_free(model, provider):
    usage = {"input_tokens": 1000, "output_tokens": 500}
    assert cost_summary(model, usage, provider) == CostSummary(0.0, False, usage)
    assert actual_cost_from_usage(model, usage, provider) is None


def test_unknown_pricing_with_no_counters_still_is_not_verified_free():
    assert cost_summary("new-model", {}) == CostSummary(0.0, False)


@pytest.mark.parametrize("provider", ["local", "mock"])
def test_explicit_free_backend_does_not_require_model_rates(provider):
    usage = {"input_tokens": 1000, "cache_read_input_tokens": 500, "cache_creation_input_tokens": 100}
    assert cost_summary("any-model", usage, provider) == CostSummary(0.0, True)


def test_hosted_mock_model_name_does_not_imply_free_billing():
    assert cost_summary("mock-developer", {"input_tokens": 10}, "openai").pricing_known is False


@pytest.mark.parametrize("provider", ["", "anthropic"])
def test_anthropic_cache_keeps_ordinary_cost_and_unresolved_cache(provider):
    usage = {
        "input_tokens": 1000, "output_tokens": 500,
        "cache_read_input_tokens": 800, "cache_creation_input_tokens": 200,
    }
    assert cost_summary("claude-sonnet-4-6", usage, provider) == CostSummary(
        0.0105, False, {"cache_read_input_tokens": 800, "cache_creation_input_tokens": 200},
    )
    assert actual_cost_from_usage("claude-sonnet-4-6", usage, provider) is None


@pytest.mark.parametrize("usage", [
    {"input_tokens": 1000, "output_tokens": 500, "cache_read_input_tokens": 800},
    {"prompt_tokens": 1000, "completion_tokens": 500, "prompt_tokens_details": {"cached_tokens": 800}},
])
def test_openai_cached_subset_is_excluded_from_known_input_cost(usage):
    assert cost_summary("gpt-4o", usage, "openai") == CostSummary(
        0.0055, False, {"cache_read_input_tokens": 800},
    )


def test_cache_only_usage_is_unresolved_not_free():
    assert cost_summary("claude-sonnet-4-6", {"cache_creation_input_tokens": 50}, "anthropic") == CostSummary(
        0.0, False, {"cache_creation_input_tokens": 50},
    )


def test_unknown_cost_is_recorded_even_with_zero_subtotal(tmp_path):
    record_run_cost(tmp_path, run_id="unknown", cost_usd=0.0, pricing_known=False)
    entry = json.loads((tmp_path / ".agent-state/budget-history.jsonl").read_text())
    assert (entry["cost_usd"], entry["pricing_known"], entry["run_id"]) == (0.0, False, "unknown")
    status = load_daily_so_far(tmp_path, daily_cap_usd=5.0)
    assert status == BudgetStatus(0.0, 5.0, entry["date"], has_unresolved_spend=True)
    assert status.remaining_usd == 0.0


def test_mixed_known_and_unresolved_ledger_retains_known_subtotal(tmp_path):
    record_run_cost(tmp_path, run_id="priced", cost_usd=0.25)
    record_run_cost(tmp_path, run_id="partial", cost_usd=0.10, pricing_known=False)
    record_run_cost(tmp_path, run_id="later-priced", cost_usd=0.20)
    status = load_daily_so_far(tmp_path, daily_cap_usd=5.0)
    assert status == BudgetStatus(0.55, 5.0, status.today, has_unresolved_spend=True)


def test_legacy_ledger_entries_remain_readable(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcrew.cost._today_iso", lambda: "2026-01-01")
    state = tmp_path / ".agent-state"
    state.mkdir()
    (state / "budget-history.jsonl").write_text('{"date":"2026-01-01","cost_usd":0.25}\n')
    assert load_daily_so_far(tmp_path, 5.0) == BudgetStatus(0.25, 5.0, "2026-01-01")


def test_previous_day_unresolved_entry_does_not_taint_today(tmp_path, monkeypatch):
    monkeypatch.setattr("agentcrew.cost._today_iso", lambda: "2026-01-01")
    record_run_cost(tmp_path, run_id="old", cost_usd=0.0, pricing_known=False)
    monkeypatch.setattr("agentcrew.cost._today_iso", lambda: "2026-01-02")
    assert load_daily_so_far(tmp_path, 5.0) == BudgetStatus(0.0, 5.0, "2026-01-02")


@pytest.mark.parametrize("cap,blocked", [(5.0, True), (0.0, False)])
def test_later_known_run_cannot_verify_cap_after_unknown_spend(tmp_path, cap, blocked):
    record_run_cost(tmp_path, run_id="unknown", cost_usd=0.0, pricing_known=False)
    estimate = RunEstimate(total_usd=0.1)
    gate = decide_cost_gate(
        estimate, load_daily_so_far(tmp_path, cap), per_run_warn_usd=0.5, per_run_block_usd=1,
    )
    assert (gate.block, gate.warn) == (blocked, False)
    if blocked:
        assert "daily cap cannot be verified" in gate.reason
        assert "unresolved" in gate.reason


@pytest.mark.parametrize("line", [
    'not-json', 'null', '[]', '{"cost_usd": 0}',
    '{"date":"2026-01-01","cost_usd":null}',
    '{"date":"2026-01-01","cost_usd":-1}',
    '{"date":"2026-01-01","cost_usd":"nan"}',
])
def test_unreadable_spend_cannot_make_cap_verifiable(tmp_path, monkeypatch, line):
    monkeypatch.setattr("agentcrew.cost._today_iso", lambda: "2026-01-01")
    state = tmp_path / ".agent-state"
    state.mkdir()
    (state / "budget-history.jsonl").write_text(line + "\n")
    assert load_daily_so_far(tmp_path, 5.0) == BudgetStatus(0.0, 5.0, "2026-01-01", True)


@pytest.mark.parametrize("cost", [-1.0, float("inf"), float("nan")])
def test_invalid_cost_is_not_persisted(tmp_path, cost):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        record_run_cost(tmp_path, run_id="invalid", cost_usd=cost)
    assert not (tmp_path / ".agent-state").exists()


@pytest.mark.parametrize("alias", ["root", "ledger", "hardlink"])
@pytest.mark.parametrize("operation", ["load", "record"])
def test_direct_budget_access_rejects_state_aliases(tmp_path, alias, operation):
    outside = tmp_path / "outside"
    outside.mkdir()
    target = outside / "ledger"
    target.write_text("protected\n")
    state = tmp_path / "project" / ".agent-state"
    state.parent.mkdir()
    if alias == "root":
        state.symlink_to(outside, target_is_directory=True)
    else:
        state.mkdir()
        ledger = state / "budget-history.jsonl"
        if alias == "ledger":
            ledger.symlink_to(target)
        else:
            os.link(target, ledger)
    with pytest.raises(UnsafeStatePath):
        if operation == "load":
            load_daily_so_far(state.parent, 1.0)
        else:
            record_run_cost(state.parent, run_id="blocked", cost_usd=0.1)
    assert target.read_text() == "protected\n"
