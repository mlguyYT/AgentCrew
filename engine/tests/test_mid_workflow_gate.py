"""Mid-workflow human-decision gate (#3)."""

from pathlib import Path

import pytest

from agentcrew.orchestrator import auto_approve, run as run_team
from agentcrew.provider import MockProvider, ScriptedTurn
from agentcrew.routing import Routing
from agentcrew.agentcrew_root import find_agentcrew_root


def test_role_after_gate_resolves_when_present():
    r = Routing(
        task="t", project="p", intent="i", risk="critical",
        lane="Full Lane plus explicit human decision",
        quality_profile="strict", recipe="bug-fix",
        starting_role="Advisor",
        workflow="Advisor -> Idea Consultant -> Human decision -> Product Manager -> Developer -> Tester -> Human",
    )
    assert r.has_mid_workflow_human_gate() is True
    assert r.role_after_mid_workflow_human_gate() == "Product Manager"


def test_role_after_gate_skips_conditional_role():
    r = Routing(
        task="t", project="p", intent="i", risk="critical",
        lane="Full Lane plus explicit human decision",
        quality_profile="strict", recipe="bug-fix",
        starting_role="Advisor",
        workflow="Advisor -> Human decision -> Reviewer if risk is meaningful -> Human",
    )
    # Reviewer's condition is true (critical risk), so it's the next acting role.
    assert r.role_after_mid_workflow_human_gate() == "Reviewer"


def test_role_after_gate_expands_specialist_placeholder():
    r = Routing(
        task="t", project="p", intent="i", risk="critical",
        lane="Full Lane plus explicit human decision",
        quality_profile="strict", recipe="bug-fix",
        starting_role="Advisor",
        workflow="Advisor -> Human decision -> Specialist Reviewer -> Human",
        specialists=["Security Reviewer"],
    )
    assert r.role_after_mid_workflow_human_gate() == "Security Reviewer"


def test_no_gate_returns_none():
    r = Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix",
        starting_role="Developer",
        workflow="Developer -> Tester -> Human",
    )
    assert r.has_mid_workflow_human_gate() is False
    assert r.role_after_mid_workflow_human_gate() is None


# --- Orchestrator integration ----------------------------------------------


def _empty_handoff(sender: str, receiver: str = "Tester", decision: str = "ready_for_test") -> dict:
    return {
        "sender": sender,
        "receiver": receiver,
        "decision": decision,
        "context": ["mock"],
        "evidence": ["mock"],
        "next_action": "next role acts",
        "open_questions": [],
    }


def _mock_for_critical_run() -> MockProvider:
    """Scripts every role the orchestrator might invoke on a critical-risk run."""
    return MockProvider(
        scripts={
            role: [ScriptedTurn(submission=_empty_handoff(role))]
            for role in (
                "Advisor", "Idea Consultant", "Product Manager",
                "Developer", "Tester", "Reviewer",
                "Security Reviewer", "Release Manager",
            )
        }
    )


@pytest.fixture
def project(tmp_path: Path) -> Path:
    p = tmp_path / "proj"
    p.mkdir()
    (p / "broken.py").write_text("x = 1\n")
    return p


def _models() -> dict[str, str]:
    return {
        role: f"mock-{role}"
        for role in (
            "Advisor", "Idea Consultant", "Product Manager",
            "Developer", "Tester", "Reviewer",
            "Security Reviewer", "Release Manager", "UX / Design Reviewer",
            "Documentation Agent", "Researcher Agent",
        )
    }


def test_risk_acceptor_called_on_critical_run(project):
    """A critical-risk task triggers risk_acceptor before the post-gate role."""
    root = find_agentcrew_root()
    seen: list[tuple[str, str]] = []

    def accept(routing, role):
        seen.append((routing.risk, role))
        return True

    result = run_team(
        task="Rotate the production secret in deploy config",
        project_dir=project,
        root=root,
        provider=_mock_for_critical_run(),
        model_for_role=_models(),
        routing_approver=auto_approve,
        risk_acceptor=accept,
    )
    # Was the risk_acceptor consulted?
    assert seen, "risk_acceptor was never called on a critical-risk run"
    assert seen[0][0] == "critical"
    # And consulted exactly once (not before every role).
    assert len(seen) == 1


def test_risk_acceptor_rejection_stops_run(project):
    root = find_agentcrew_root()

    def reject(_routing, _role):
        return False

    result = run_team(
        task="Rotate the production secret in deploy config",
        project_dir=project,
        root=root,
        provider=_mock_for_critical_run(),
        model_for_role=_models(),
        routing_approver=auto_approve,
        risk_acceptor=reject,
    )
    assert result.final_decision == "mid_workflow_human_decision_rejected"
    assert result.next_owner == "human"
    # No further roles ran after the gate (only Advisor + Idea Consultant
    # which precede the Human decision marker).
    senders_after_gate = {h.sender for h in result.handoffs}
    assert "Product Manager" not in senders_after_gate
    assert "Developer" not in senders_after_gate


def test_risk_acceptor_not_called_on_low_risk(project):
    """Low-risk runs never hit the mid-workflow gate."""
    root = find_agentcrew_root()
    called = []

    def watch(routing, role):
        called.append((routing.risk, role))
        return True

    from agentcrew.demo_script import demo_provider

    result = run_team(
        task="Fix broken.py so add_numbers returns a + b",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role=_models(),
        routing_approver=auto_approve,
        risk_acceptor=watch,
    )
    assert called == []  # never consulted
    assert result.final_decision == "ready_for_human_approval"
