"""Regression coverage for reviewed continuation, approval, and billing paths."""

import json
from unittest.mock import Mock

import pytest

from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew import cli
from agentcrew.config import BudgetConfig, ProjectConfig
from agentcrew.continuation import load_continuation, write_continuation
from agentcrew.cost import load_daily_so_far, record_run_cost
from agentcrew.handoff import Handoff
from agentcrew.orchestrator import run
from agentcrew.provider import MockProvider, ScriptedTurn
from agentcrew.provider_openai import OpenAICompatibleProvider
from agentcrew.provider_local import LocalProvider
from agentcrew.routing import Routing, classify


def submission(sender="Product Manager", decision="ready_for_human_approval", receiver="Human"):
    return {"sender": sender, "receiver": receiver, "decision": decision,
            "context": ["Synthetic review regression"], "next_action": "Continue safely"}


def route(project, workflow="Product Manager -> Human", *, direct=False):
    return Routing(task="Should I use SSE for this?" if direct else "Review the plan",
                   project=str(project), intent="advisory" if direct else "review", risk="low",
                   lane="Direct Answer Mode" if direct else "Full Lane", quality_profile="standard",
                   recipe="review", starting_role="None" if direct else "Product Manager",
                   workflow="Direct answer -> Human" if direct else workflow)


def metered_provider(responses):
    provider = OpenAICompatibleProvider(api_key="offline-placeholder")
    provider._post = Mock(side_effect=responses)
    return provider


def response(arguments, tool="submit_handoff"):
    return {"choices": [{"finish_reason": "tool_calls", "message": {"content": None,
            "tool_calls": [{"id": "fixture", "type": "function", "function": {
                "name": tool, "arguments": json.dumps(arguments),
            }}]}}], "usage": {"prompt_tokens": 1000, "completion_tokens": 100}}


@pytest.mark.parametrize("legacy", [False, True])
def test_product_idea_continuation_keeps_security_reviewer(tmp_path, legacy):
    routing = classify(find_agentcrew_root(), task="I want to add team billing to this app. Help me shape it and implement the first safe version.", project=str(tmp_path))
    directory = tmp_path / ".agent-state" / "runs" / "planning"
    directory.mkdir(parents=True)
    artifact = write_continuation(directory, routing=routing, handoffs=[Handoff(**submission(decision="needs_human_decision"))])
    if legacy:
        payload = json.loads(artifact.read_text())
        payload["remaining_workflow"] = routing.workflow_after_mid_workflow_human_gate()
        artifact.write_text(json.dumps(payload))
    continuation = load_continuation(tmp_path, "planning")
    assert "Security Reviewer" in continuation.routing.acting_roles_in_order()


def test_completed_planning_specialist_is_not_appended_again(tmp_path):
    routing = route(tmp_path, "Researcher Agent -> Product Manager -> Human decision -> Documentation Agent -> Human")
    routing.specialists = ["Researcher Agent"]
    directory = tmp_path / ".agent-state" / "runs" / "planning"
    directory.mkdir(parents=True)
    write_continuation(directory, routing=routing, handoffs=[Handoff(**submission("Researcher Agent")), Handoff(**submission())])
    assert load_continuation(tmp_path, "planning").routing.acting_roles_in_order() == ["Documentation Agent"]


@pytest.mark.parametrize("bad", ["sender", "receiver", "null"])
def test_invalid_specialist_identity_stops_with_usage_preserved(tmp_path, bad):
    routing = route(tmp_path, "Product Manager -> Security Reviewer -> Human")
    routing.specialists = ["Security Reviewer"]
    malformed = submission("Unknown Role" if bad == "sender" else "Security Reviewer", "rework_required",
                           "Unknown Role" if bad == "receiver" else "Product Manager")
    provider = metered_provider([response(submission()), response(None if bad == "null" else malformed)])
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={role: "gpt-4o" for role in routing.acting_roles_in_order()})
    assert result.final_decision.startswith("specialist_protocol_failure")
    assert result.actual_cost_usd == pytest.approx(0.007)
    assert load_daily_so_far(tmp_path, 1).daily_so_far_usd == pytest.approx(0.007)
    assert provider._post.call_count == 2


def test_free_advisor_preview_uses_actual_role_and_returns_answer(tmp_path, monkeypatch):
    provider = MockProvider({"Advisor": [ScriptedTurn(submission={"answer": "Use SSE."})]})
    events = []
    monkeypatch.setattr(cli, "_emit", events.append)
    result = cli._run_from_agent(task="Should I use SSE for this?", project=tmp_path,
        root=find_agentcrew_root(), provider=provider, models={"Advisor": "mock-advisor"},
        routing_approver=lambda _: True, routing_override=route(tmp_path, direct=True))
    assert result == 0
    assert "cost_approval_required" not in [event["event"] for event in events]
    preview = next(event for event in events if event["event"] == "cost_preview")
    assert preview["per_role"][0]["role"] == "Advisor"
    assert events[-1]["answer"] == "Use SSE."
    assert not (tmp_path / ".agent-state").exists()


def test_unconfigured_advisor_does_not_request_cost_approval(tmp_path, monkeypatch):
    events = []
    monkeypatch.setattr(cli, "_emit", events.append)
    assert cli._run_from_agent(task="Should I use SSE?", project=tmp_path, root=find_agentcrew_root(),
        provider=MockProvider({}), models={}, routing_approver=lambda _: True,
        routing_override=route(tmp_path, direct=True)) == 0
    assert "cost_approval_required" not in [event["event"] for event in events]
    assert events[-1]["final_decision"] == "direct_answer_or_advisory"
    assert not (tmp_path / ".agent-state").exists()


@pytest.mark.parametrize("valid", [True, False])
def test_paid_advisor_is_accounted_even_when_answer_invalid(tmp_path, valid):
    provider = metered_provider([response({"answer": "An answer"} if valid else None, "submit_answer")])
    routing = route(tmp_path, direct=True)
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={"Advisor": "gpt-4o"})
    assert result.final_decision == ("answered" if valid else "direct_answer_or_advisory_protocol_failure")
    assert result.actual_cost_usd == pytest.approx(0.0035)
    assert load_daily_so_far(tmp_path, 1).daily_so_far_usd == pytest.approx(0.0035)
    assert sorted(p.name for p in (tmp_path / ".agent-state").iterdir()) == ["budget-history.jsonl"]


def test_paid_advisor_budget_rejection_precedes_model_call(tmp_path, monkeypatch):
    provider = metered_provider([])
    monkeypatch.setattr(ProjectConfig, "load", lambda _: ProjectConfig(budget=BudgetConfig(daily_max_usd=0.0001)))
    approver = Mock(return_value=False)
    routing = route(tmp_path, direct=True)
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={"Advisor": "gpt-4o"}, cost_approver=approver)
    assert result.final_decision == "cost_rejected_by_human"
    assert approver.call_count == 1
    assert provider._post.call_count == 0
    assert not (tmp_path / ".agent-state").exists()


def test_unpriced_advisor_keeps_usage_in_ledger_without_workflow_artifacts(tmp_path):
    provider = metered_provider([response({"answer": "An answer"}, "submit_answer")])
    routing = route(tmp_path, direct=True)
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={"Advisor": "unpriced-model"}, cost_approver=lambda _: True)
    assert result.final_decision == "answered"
    ledger = json.loads((tmp_path / ".agent-state" / "budget-history.jsonl").read_text())
    assert ledger["pricing_known"] is False
    assert ledger["unresolved_usage"][0]["usage"]["input_tokens"] == 1000
    assert ledger["unresolved_usage"][0]["model"] == "unpriced-model"
    assert sorted(p.name for p in (tmp_path / ".agent-state").iterdir()) == ["budget-history.jsonl"]


@pytest.mark.parametrize("model", ["gpt-4o", "unpriced-model"])
def test_resume_requires_fresh_cost_approval_and_can_retry(tmp_path, monkeypatch, model):
    routing = route(tmp_path, "Product Manager -> Human execution approval -> Documentation Agent -> Human")
    directory = tmp_path / ".agent-state" / "runs" / "planning"
    directory.mkdir(parents=True)
    write_continuation(directory, routing=routing, handoffs=[])
    record_run_cost(tmp_path, run_id="prior", cost_usd=2)
    config_dir = tmp_path / ".agentcrew"
    config_dir.mkdir()
    (config_dir / "config.yaml").write_text("backend: openai\nbudget:\n  daily_max_usd: 1.0\n")
    monkeypatch.setattr(cli, "_resolve_models", lambda _: {"Documentation Agent": model})
    provider = metered_provider([response(submission("Documentation Agent"))])
    monkeypatch.setattr(cli, "_make_provider", lambda _: provider)
    events = []
    monkeypatch.setattr(cli, "_emit", events.append)
    args = ["run", "--project", str(tmp_path), "--backend", "openai", "--from-agent", "--continue-run", "planning", "--approve-decision"]
    assert cli.main(args) == 1
    assert events[-1]["event"] == "cost_approval_required"
    assert provider._post.call_count == 0
    assert "resumed_run_id" not in json.loads((directory / "continuation.json").read_text())
    assert cli.main([*args, "--approve-cost"]) == 0
    assert provider._post.call_count == 1


def test_local_advisor_needs_no_cost_approval_or_state(tmp_path, monkeypatch):
    provider = LocalProvider(probe=False)
    provider._post = Mock(return_value=response({"answer": "Local answer"}, "submit_answer"))
    events = []
    monkeypatch.setattr(cli, "_emit", events.append)
    assert cli._run_from_agent(task="Should I use SSE?", project=tmp_path, root=find_agentcrew_root(),
        provider=provider, models={"Advisor": "qwen2.5:7b"}, routing_approver=lambda _: True,
        routing_override=route(tmp_path, direct=True)) == 0
    assert "cost_approval_required" not in [event["event"] for event in events]
    assert events[-1]["answer"] == "Local answer"
    assert not (tmp_path / ".agent-state").exists()


def test_compatible_gateway_does_not_inherit_official_model_pricing(tmp_path, monkeypatch):
    provider = OpenAICompatibleProvider(base_url="https://example.invalid/v1", api_key="offline-placeholder")
    provider._post = Mock()
    events = []
    monkeypatch.setattr(cli, "_emit", events.append)
    assert cli._run_from_agent(task="Should I use SSE?", project=tmp_path, root=find_agentcrew_root(),
        provider=provider, models={"Advisor": "gpt-4o"}, routing_approver=lambda _: True,
        routing_override=route(tmp_path, direct=True)) == 1
    assert events[-1]["event"] == "cost_approval_required"
    assert provider._post.call_count == 0


def test_second_planning_handoff_saves_only_current_remaining_phase(tmp_path):
    routing = route(tmp_path, "Product Manager -> Human concept approval -> Advisor -> Product Manager -> Human execution approval -> Documentation Agent -> Human")
    provider = MockProvider({
        "Product Manager": [ScriptedTurn(submission=submission(decision="ready_for_next_role")),
                            ScriptedTurn(submission=submission(decision="needs_human_decision"))],
        "Advisor": [ScriptedTurn(submission=submission("Advisor", "ready_for_next_role"))],
    })
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={role: "mock" for role in routing.acting_roles_in_order()},
                 risk_acceptor=lambda *_: True)
    assert result.final_decision == "needs_human_decision"
    assert result.remaining_workflow == "Documentation Agent -> Human"
    write_continuation(result.run_dir, routing=routing, handoffs=result.handoffs,
                       remaining_workflow=result.remaining_workflow, pending_decision=result.pending_human_decision)
    assert load_continuation(tmp_path, result.run_id).routing.acting_roles_in_order() == ["Documentation Agent"]


def test_cache_uncertainty_survives_ledger_and_presentation(tmp_path):
    from agentcrew.audit import collect, render
    from agentcrew.show import render_run
    class CachedMock(MockProvider):
        def run_agent(self, **kwargs):
            result = super().run_agent(**kwargs)
            result.provider = "anthropic"
            result.usage = {"input_tokens": 0, "output_tokens": 10, "cache_creation_input_tokens": 1_000_000}
            return result
    provider = CachedMock({"Product Manager": [ScriptedTurn(submission=submission())]})
    routing = route(tmp_path)
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={"Product Manager": "claude-sonnet-4-6"})
    assert not result.pricing_known
    assert result.actual_cost_usd == pytest.approx(0.00015)
    assert load_daily_so_far(tmp_path, 1).has_unresolved_spend
    assert "unresolved usage" in render_run(result.run_dir)
    assert "Unresolved:" in render(collect(tmp_path))


def test_provider_failure_keeps_known_usage_and_uncertain_failed_request(tmp_path):
    import httpx
    provider = metered_provider([response({"path": "missing.md"}, "read_file"), httpx.ReadTimeout("offline fixture")])
    routing = route(tmp_path)
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={"Product Manager": "gpt-4o"})
    assert result.final_decision == "protocol_failure"
    assert result.actual_cost_usd == pytest.approx(0.0035)
    assert not result.pricing_known
    assert load_daily_so_far(tmp_path, 1).has_unresolved_spend


def test_unpriced_usage_is_preserved_and_later_cap_is_unverifiable(tmp_path, monkeypatch):
    provider = metered_provider([response(submission())])
    routing = route(tmp_path)
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                 routing_override=routing, model_for_role={"Product Manager": "unpriced-model"}, cost_approver=lambda _: True)
    assert not result.pricing_known
    actual = json.loads((result.run_dir / "cost-actual.json").read_text())
    assert actual["actual_cost_usd"] is None
    assert actual["unresolved_usage"][0]["usage"]["input_tokens"] == 1000
    assert load_daily_so_far(tmp_path, 1).has_unresolved_spend
    monkeypatch.setattr(ProjectConfig, "load", lambda _: ProjectConfig(budget=BudgetConfig(daily_max_usd=1)))
    blocked = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(), provider=provider,
                  routing_override=routing, model_for_role={"Product Manager": "gpt-4o"})
    assert blocked.final_decision == "cost_rejected_by_human"
    assert provider._post.call_count == 1
