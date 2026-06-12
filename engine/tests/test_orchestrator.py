"""End-to-end test: the real classifier + mocked LLM + the example task.

This is the load-bearing test. It proves the architecture:
  - the classifier script decides the workflow
  - the engine's orchestrator follows it
  - The mocked Developer + Tester scripts execute their tools
  - Artifacts land in state-artifacts.md schema
"""

import shutil
from pathlib import Path

import pytest

from agentcrew.demo_script import demo_provider
from agentcrew.orchestrator import auto_approve, run as run_team
from agentcrew.agentcrew_root import find_agentcrew_root


@pytest.fixture
def project(tmp_path: Path) -> Path:
    proj = tmp_path / "example"
    proj.mkdir()
    (proj / "broken.py").write_text("def add_numbers(a, b):\n    return a - b\n")
    return proj


def _model_for_every_role() -> dict[str, str]:
    return {
        role: f"mock-{role.lower().replace(' / ', '-').replace(' ', '-')}"
        for role in (
            "Developer", "Tester", "Reviewer", "Security Reviewer",
            "UX / Design Reviewer", "Documentation Agent", "Researcher Agent",
            "Support Triage Agent", "Release Manager",
        )
    }


def test_classifier_drives_workflow_end_to_end(project):
    root = find_agentcrew_root()
    result = run_team(
        task="Fix broken.py so add_numbers(a, b) returns a + b",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )
    # the classifier should have classified this as Fast Lane, bug-fix recipe,
    # Developer → Tester → Human workflow.
    assert result.routing.lane == "Fast Lane"
    assert result.routing.recipe == "bug-fix"
    assert result.routing.starting_role == "Developer"
    assert result.routing.acting_roles_in_order() == ["Developer", "Tester"]

    # Both acting roles ran.
    assert [h.sender for h in result.handoffs] == ["Developer", "Tester"]

    # Final state is at human gate.
    assert result.final_decision == "ready_for_human_approval"
    assert result.next_owner == "human"

    # Developer's edit actually landed.
    assert "return a + b" in (project / "broken.py").read_text()

    # the state-artifacts schema files exist
    state_dir = project / ".agent-state"
    assert (state_dir / "current-task.md").exists()
    assert (state_dir / "handoff.md").exists()
    # Tester is mapped to test-report.md per the methodology
    assert (state_dir / "test-report.md").exists()
    # Run dir contains a task-routing.md
    assert (result.run_dir / "task-routing.md").exists()


def test_routing_rejected_by_human_stops_execution(project):
    root = find_agentcrew_root()
    rejected = []

    def reject(routing) -> bool:
        rejected.append(routing.lane)
        return False

    result = run_team(
        task="anything",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role=_model_for_every_role(),
        routing_approver=reject,
    )
    assert result.final_decision == "routing_rejected_by_human"
    assert result.next_owner == "human"
    assert result.handoffs == []
    assert len(rejected) == 1
    # Source untouched
    assert "return a - b" in (project / "broken.py").read_text()


def test_direct_answer_mode_short_circuits(project, tmp_path):
    """Advisory questions bypass the workflow entirely (Direct Answer Mode)."""
    root = find_agentcrew_root()
    result = run_team(
        task="Should I use SSE or websockets for the dashboard?",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )
    assert result.routing.lane == "Direct Answer Mode"
    assert result.final_decision == "direct_answer_or_advisory"
    assert result.handoffs == []  # no roles acted
