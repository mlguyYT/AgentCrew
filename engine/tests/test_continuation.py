from pathlib import Path

import pytest

from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew.continuation import (
    load_continuation,
    mark_continuation_resumed,
    write_continuation,
)
from agentcrew.demo_script import demo_provider
from agentcrew.handoff import Handoff
from agentcrew.orchestrator import auto_approve, run as run_team
from agentcrew.routing import Routing


def _routing(project: Path) -> Routing:
    return Routing(
        task="Build the approved product",
        project=project.name,
        intent="idea_to_product_delivery",
        risk="medium",
        lane="Full Lane",
        quality_profile="standard",
        recipe="feature",
        starting_role="Advisor",
        workflow=(
            "Advisor -> Idea Consultant -> Product Manager -> Human decision -> "
            "Developer -> Tester -> Human"
        ),
        human_decisions=[
            "approve product direction and execution boundary",
            "final approval before merge",
        ],
    )


def _planning_handoff() -> Handoff:
    return Handoff(
        sender="Product Manager",
        receiver="Human",
        decision="needs_human_decision",
        context=["MVP is scoped."],
        evidence=["Acceptance outcomes are defined."],
        next_action="CEO approves execution.",
    )


def test_continuation_starts_after_human_gate(tmp_path: Path):
    project = tmp_path / "project"
    run_dir = project / ".agent-state" / "runs" / "run_123"
    run_dir.mkdir(parents=True)
    routing = _routing(project)
    prior = _planning_handoff()
    write_continuation(run_dir, routing=routing, handoffs=[prior])

    continuation = load_continuation(project, "run_123")

    assert continuation.routing.workflow == "Developer -> Tester -> Human"
    assert continuation.routing.starting_role == "Developer"
    assert continuation.routing.acting_roles_in_order() == ["Developer", "Tester"]
    assert continuation.routing.human_decisions == ["final approval before merge"]
    assert continuation.prior_handoffs == (prior,)
    assert (
        continuation.pending_decision
        == "approve product direction and execution boundary"
    )


def test_continuation_rejects_path_traversal(tmp_path: Path):
    with pytest.raises(ValueError, match="invalid continuation run id"):
        load_continuation(tmp_path, "../other-project")


def test_completed_continuation_cannot_be_replayed(tmp_path: Path):
    project = tmp_path / "project"
    run_dir = project / ".agent-state" / "runs" / "run_123"
    run_dir.mkdir(parents=True)
    write_continuation(
        run_dir,
        routing=_routing(project),
        handoffs=[_planning_handoff()],
    )

    mark_continuation_resumed(project, "run_123", "run_456")

    with pytest.raises(ValueError, match="already resumed by run run_456"):
        load_continuation(project, "run_123")


def test_orchestrator_continues_with_prior_planning_handoff(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "broken.py").write_text(
        "def add_numbers(a, b):\n    return a - b\n"
    )
    (project / "test_broken.py").write_text(
        "import unittest\n"
        "from broken import add_numbers\n\n"
        "class AddNumbersTest(unittest.TestCase):\n"
        "    def test_adds(self):\n"
        "        self.assertEqual(add_numbers(2, 3), 5)\n"
    )
    routing = _routing(project)
    routing.workflow = "Developer -> Tester -> Human"
    routing.starting_role = "Developer"
    prior = _planning_handoff()

    result = run_team(
        task=routing.task,
        project_dir=project,
        root=find_agentcrew_root(),
        provider=demo_provider(),
        model_for_role={
            "Developer": "mock-developer",
            "Tester": "mock-tester",
        },
        routing_approver=auto_approve,
        routing_override=routing,
        prior_handoffs=[prior],
        approved_human_decision=(
            "approve product direction and execution boundary"
        ),
        ceo_profile_path=tmp_path / "missing-profile",
    )

    assert [handoff.sender for handoff in result.handoffs] == [
        "Product Manager",
        "Developer",
        "Tester",
    ]
    assert result.final_decision == "ready_for_human_approval"
    assert "approved: approve product direction" in (
        project / ".agent-state" / "human-decisions.md"
    ).read_text()
