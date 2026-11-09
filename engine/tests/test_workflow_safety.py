"""Approval and specialist outcomes remain authoritative during coordination."""

import pytest

from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew.command_sandbox import SandboxUnavailable
from agentcrew.cli import _run_exit_code
from agentcrew.continuation import load_continuation, write_continuation
from agentcrew.orchestrator import run
from agentcrew.provider import MockProvider, ScriptedTurn
from agentcrew.routing import Routing


def submission(sender, decision="ready_for_human_approval", receiver="Human"):
    return {"sender": sender, "receiver": receiver, "decision": decision,
            "context": ["Synthetic workflow fixture"], "next_action": "Continue the approved work"}


def execute(project, workflow, scripts, *, specialists=(), accept=lambda *_: False, provider=None):
    routing = Routing(
        task="Review the project plan", project=str(project), intent="review", risk="medium",
        lane="Full Lane", quality_profile="standard", recipe="review",
        starting_role=workflow.split(" -> ")[0], workflow=workflow, specialists=list(specialists),
    )
    models = {role: "mock-role" for role in routing.acting_roles_in_order()}
    return run(task=routing.task, project_dir=project, root=find_agentcrew_root(),
               provider=provider or MockProvider(scripts), model_for_role=models,
               routing_override=routing, risk_acceptor=accept)


@pytest.mark.parametrize("resolved", [True, False])
def test_parallel_specialist_rework_returns_to_owner_and_rechecks_team(tmp_path, resolved):
    scripts = {
        "Product Manager": [ScriptedTurn(submission=submission("Product Manager")) for _ in range(2)],
        "Security Reviewer": [
            ScriptedTurn(submission=submission("Security Reviewer", "rework_required", "Product Manager")),
            ScriptedTurn(submission=submission(
                "Security Reviewer", "ready_for_human_approval" if resolved else "rework_required", "Product Manager")),
        ],
        "Documentation Agent": [ScriptedTurn(submission=submission("Documentation Agent")) for _ in range(2)],
    }
    result = execute(tmp_path, "Product Manager -> Security Reviewer -> Documentation Agent -> Human",
                     scripts, specialists=["Security Reviewer", "Documentation Agent"])
    assert [h.sender for h in result.handoffs].count("Product Manager") == 2
    assert [h.sender for h in result.handoffs].count("Security Reviewer") == 2
    if resolved:
        assert result.final_decision == "ready_for_human_approval"
        assert [h.sender for h in result.handoffs].count("Documentation Agent") == 2
    else:
        assert result.final_decision == "rework_limit_exceeded:Security Reviewer"


def test_gate_before_parallel_suffix_stops_specialists(tmp_path):
    scripts = {"Product Manager": [ScriptedTurn(submission=submission("Product Manager"))]}
    seen = []
    def reject(routing, role):
        seen.append(role)
        return False
    result = execute(tmp_path, "Product Manager -> Human scope approval -> Security Reviewer -> Human",
                     scripts, specialists=["Security Reviewer"], accept=reject)
    assert seen == ["Security Reviewer"]
    assert result.final_decision == "mid_workflow_human_decision_required"
    assert [h.sender for h in result.handoffs] == ["Product Manager"]
    assert result.remaining_workflow == "Security Reviewer -> Human"


def test_second_gate_is_not_covered_by_first_approval_and_resumes_correct_suffix(tmp_path):
    scripts = {
        "Advisor": [ScriptedTurn(submission=submission("Advisor", "ready_for_next_role"))],
        "Product Manager": [ScriptedTurn(submission=submission("Product Manager", "ready_for_next_role"))],
    }
    seen = []
    def accept_first(routing, role):
        seen.append((role, routing.human_decisions[0]))
        return len(seen) == 1
    result = execute(
        tmp_path,
        "Advisor -> Human concept approval -> Product Manager -> Human execution approval -> Product Manager -> Security Reviewer -> Human",
        scripts, specialists=["Security Reviewer"], accept=accept_first,
    )
    assert seen == [("Product Manager", "Human concept approval"), ("Product Manager", "Human execution approval")]
    assert result.final_decision == "mid_workflow_human_decision_required"
    assert [h.sender for h in result.handoffs] == ["Advisor", "Product Manager"]
    write_continuation(result.run_dir, routing=result.routing, handoffs=result.handoffs,
                       remaining_workflow=result.remaining_workflow,
                       pending_decision=result.pending_human_decision)
    continuation = load_continuation(tmp_path, result.run_id)
    assert continuation.routing.workflow == "Product Manager -> Security Reviewer -> Human"
    assert continuation.pending_decision == "Human execution approval"


def test_parallel_accounting_keeps_usage_even_without_a_handoff(tmp_path):
    class MeteredMock(MockProvider):
        def run_agent(self, **kwargs):
            result = super().run_agent(**kwargs)
            result.model = "gpt-4o"
            result.provider = "openai"
            result.usage = {"input_tokens": 100, "output_tokens": 10}
            return result
    scripts = {
        "Product Manager": [ScriptedTurn(submission=submission("Product Manager"))],
        "Security Reviewer": [ScriptedTurn(submission=None)],
        "Documentation Agent": [ScriptedTurn(submission=submission("Documentation Agent"))],
    }
    # Use a declared metered model so role attribution survives invalid output.
    routing = Routing(task="Review plan", project=str(tmp_path), intent="review", risk="medium",
                      lane="Full Lane", quality_profile="standard", recipe="review",
                      starting_role="Product Manager",
                      workflow="Product Manager -> Security Reviewer -> Documentation Agent -> Human",
                      specialists=["Security Reviewer", "Documentation Agent"])
    result = run(task=routing.task, project_dir=tmp_path, root=find_agentcrew_root(),
                 provider=MeteredMock(scripts), routing_override=routing,
                 model_for_role={role: "gpt-4o" for role in routing.acting_roles_in_order()})
    assert result.final_decision == "specialist_protocol_failure:Security Reviewer"
    assert len(result.agent_runs) == 3
    assert result.actual_cost_usd == pytest.approx(3 * 0.00035)


def test_unavailable_isolation_stops_before_any_model_call(tmp_path, monkeypatch):
    def unavailable(_project):
        raise SandboxUnavailable("No isolation support")
    monkeypatch.setattr("agentcrew.orchestrator.check_sandbox", unavailable)
    result = execute(tmp_path, "Developer -> Tester -> Human", {})
    assert result.final_decision == "command_sandbox_unavailable"
    assert result.agent_runs == []
    assert _run_exit_code(result) == 1
    assert "No isolation support" in (result.run_dir / "error.md").read_text()
