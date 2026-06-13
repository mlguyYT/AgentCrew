"""Direct Answer Mode invokes the Advisor without creating state artifacts."""

from pathlib import Path

import pytest

from agentcrew.demo_script import demo_provider
from agentcrew.orchestrator import auto_approve, run as run_team
from agentcrew.provider import MockProvider, ScriptedTurn
from agentcrew.agentcrew_root import find_agentcrew_root


@pytest.fixture
def project(tmp_path: Path) -> Path:
    p = tmp_path / "proj"
    p.mkdir()
    (p / "broken.py").write_text("# placeholder\n")
    return p


def _all_models() -> dict[str, str]:
    return {
        role: f"mock-{role}"
        for role in (
            "Advisor", "Idea Consultant", "Product Manager",
            "Developer", "Tester", "Reviewer",
            "Security Reviewer", "Release Manager",
            "UX / Design Reviewer", "Documentation Agent",
            "Researcher Agent", "Support Triage Agent", "LLM Agent",
            "CNN Agent", "Skill Validator",
        )
    }


def test_advisor_runs_in_direct_answer_mode_without_state(project):
    root = find_agentcrew_root()
    result = run_team(
        task="Should I use SSE or websockets for the dashboard?",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role=_all_models(),
        routing_approver=auto_approve,
    )
    assert result.routing.is_direct_answer()
    assert result.final_decision == "answered"
    assert result.next_owner == "human"
    assert "SSE" in result.direct_answer or "Server-Sent Events" in result.direct_answer
    assert not (project / ".agent-state").exists()


def test_advisor_missing_model_falls_back_to_routing_only(project):
    """If the caller didn't supply an Advisor model, the engine still returns the routing."""
    root = find_agentcrew_root()
    result = run_team(
        task="Should I use SSE or websockets for the dashboard?",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        # Note: no Advisor in the models dict
        model_for_role={"Developer": "mock-dev"},
        routing_approver=auto_approve,
    )
    assert result.routing.is_direct_answer()
    assert result.final_decision == "direct_answer_or_advisory"
    assert result.direct_answer == ""
    assert not (project / ".agent-state").exists()


def test_advisor_protocol_failure_surfaces_cleanly(project):
    root = find_agentcrew_root()
    bad = MockProvider(
        scripts={
            "Advisor": [ScriptedTurn()],  # no submission
        }
    )
    result = run_team(
        task="Should I use SSE or websockets for the dashboard?",
        project_dir=project,
        root=root,
        provider=bad,
        model_for_role=_all_models(),
        routing_approver=auto_approve,
    )
    assert result.final_decision == "direct_answer_or_advisory_protocol_failure"
    assert result.direct_answer == ""
    assert not (project / ".agent-state").exists()
