"""End-to-end test: the real classifier + mocked LLM + the example task.

This is the load-bearing test. It proves the architecture:
  - the classifier script decides the workflow
  - the engine's orchestrator follows it
  - The mocked Developer + Tester scripts execute their tools
  - Artifacts land in state-artifacts.md schema
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from agentcrew.demo_script import demo_provider
from agentcrew.orchestrator import auto_approve, run as run_team
from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew.provider import MockProvider, ScriptedTurn
from agentcrew.routing import Routing


@pytest.fixture
def project(tmp_path: Path) -> Path:
    proj = tmp_path / "example"
    proj.mkdir()
    (proj / "broken.py").write_text("def add_numbers(a, b):\n    return a - b\n")
    (proj / "test_broken.py").write_text(
        "import unittest\n"
        "from broken import add_numbers\n\n"
        "class AddNumbersTest(unittest.TestCase):\n"
        "    def test_adds(self):\n"
        "        self.assertEqual(add_numbers(2, 3), 5)\n"
    )
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
    assert result.agent_runs[0].context_fragments[0] == (
        "playbook:developer-execution-loop"
    )
    assert "recipe:bug-fix" in result.agent_runs[0].context_fragments
    assert result.agent_runs[0].context_estimated_tokens <= 1_200
    assert result.agent_runs[1].context_fragments[0] == (
        "playbook:tester-validation-loop"
    )
    assert result.agent_runs[1].context_estimated_tokens <= 1_200
    assert result.agent_runs[1].validation_evidence["validation"][
        "status"
    ] == "passed"

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
    assert len(
        list(result.run_dir.glob("*-execution-evidence.json"))
    ) == 1
    assert len(
        list(result.run_dir.glob("*-validation-evidence.json"))
    ) == 1


def test_bundled_mock_example_runs_from_its_failing_baseline(tmp_path):
    source = (
        Path(__file__).resolve().parent.parent
        / "examples"
        / "01_python_bug_fix"
    )
    project = tmp_path / "example"
    shutil.copytree(source, project)

    assert "return a - b" in (project / "broken.py").read_text()
    result = run_team(
        task=(project / "task.txt").read_text().strip(),
        project_dir=project,
        root=find_agentcrew_root(),
        provider=demo_provider(),
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )

    assert result.final_decision == "ready_for_human_approval"
    assert "return a + b" in (project / "broken.py").read_text()


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


def test_developer_self_corrects_missing_validation(project):
    provider = MockProvider(
        scripts={
            "Developer": [
                ScriptedTurn(
                    tool_calls=[
                        {"name": "read_file", "input": {"path": "broken.py"}},
                        {
                            "name": "edit_file",
                            "input": {
                                "path": "broken.py",
                                "old_string": "return a - b",
                                "new_string": "return a + b",
                            },
                        },
                    ],
                    submission={
                        "sender": "Developer",
                        "receiver": "Tester",
                        "decision": "ready_for_test",
                        "next_action": "Tester validates the change.",
                    },
                ),
                ScriptedTurn(
                    tool_calls=[
                        {
                            "name": "bash",
                            "input": {
                                "command": "python3 -m py_compile broken.py"
                            },
                        },
                    ],
                    submission={
                        "sender": "Developer",
                        "receiver": "Tester",
                        "decision": "ready_for_test",
                        "next_action": "Tester validates the change.",
                    },
                ),
            ],
            "Tester": [
                ScriptedTurn(
                    tool_calls=[
                        {
                            "name": "bash",
                            "input": {
                                "command": (
                                    "python3 -m unittest -q"
                                ),
                            },
                        },
                    ],
                    submission={
                        "sender": "Tester",
                        "receiver": "Human",
                        "decision": "ready_for_human_approval",
                        "next_action": "Human reviews the evidence.",
                    },
                ),
            ],
        }
    )
    result = run_team(
        task="Fix broken.py so add_numbers(a, b) returns a + b",
        project_dir=project,
        root=find_agentcrew_root(),
        provider=provider,
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )

    assert [handoff.sender for handoff in result.handoffs] == [
        "Developer",
        "Developer",
        "Tester",
    ]
    assert result.handoffs[0].decision == "rework_required"
    assert result.handoffs[1].validation_status == "passed"
    assert result.final_decision == "ready_for_human_approval"
    evidence_files = sorted(result.run_dir.glob("*-execution-evidence.json"))
    assert len(evidence_files) == 2
    second_evidence = json.loads(evidence_files[1].read_text())
    assert second_evidence["observed_changed_files"] == ["broken.py"]


def test_tester_self_corrects_missing_validation(project):
    provider = demo_provider()
    provider._scripts["Tester"] = [
        ScriptedTurn(
            submission={
                "sender": "Tester",
                "receiver": "Human",
                "decision": "ready_for_human_approval",
                "next_action": "Human reviews the evidence.",
            },
        ),
        ScriptedTurn(
            tool_calls=[
                {
                    "name": "bash",
                    "input": {"command": "python3 -m unittest -q"},
                }
            ],
            submission={
                "sender": "Tester",
                "receiver": "Human",
                "decision": "ready_for_human_approval",
                "next_action": "Human reviews the evidence.",
            },
        ),
    ]

    result = run_team(
        task="Fix broken.py so add_numbers(a, b) returns a + b",
        project_dir=project,
        root=find_agentcrew_root(),
        provider=provider,
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )

    tester_handoffs = [
        handoff for handoff in result.handoffs if handoff.sender == "Tester"
    ]
    assert [handoff.decision for handoff in tester_handoffs] == [
        "rework_required",
        "ready_for_human_approval",
    ]
    assert tester_handoffs[0].receiver == "Tester"
    assert tester_handoffs[1].validation_status == "passed"
    assert len(
        list(result.run_dir.glob("*-validation-evidence.json"))
    ) == 2


def test_tester_process_retry_does_not_consume_developer_rework_route(project):
    provider = demo_provider()
    provider._scripts["Developer"].append(
        ScriptedTurn(
            tool_calls=[
                {
                    "name": "bash",
                    "input": {"command": "python3 -m py_compile broken.py"},
                }
            ],
            submission={
                "sender": "Developer",
                "receiver": "Tester",
                "decision": "ready_for_test",
                "next_action": "Tester reruns the failed check.",
            },
        )
    )
    tester_submission = {
        "sender": "Tester",
        "receiver": "Human",
        "decision": "ready_for_human_approval",
        "next_action": "Human reviews the evidence.",
    }
    provider._scripts["Tester"] = [
        ScriptedTurn(submission=tester_submission),
        ScriptedTurn(
            tool_calls=[
                {
                    "name": "bash",
                    "input": {
                        "command": (
                            "python3 -m unittest -q "
                            "test_broken.MissingTest"
                        )
                    },
                }
            ],
            submission=tester_submission,
        ),
        ScriptedTurn(
            tool_calls=[
                {
                    "name": "bash",
                    "input": {"command": "python3 -m unittest -q"},
                }
            ],
            submission=tester_submission,
        ),
    ]

    result = run_team(
        task="Fix broken.py so add_numbers(a, b) returns a + b",
        project_dir=project,
        root=find_agentcrew_root(),
        provider=provider,
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )

    assert [handoff.sender for handoff in result.handoffs] == [
        "Developer",
        "Tester",
        "Tester",
        "Developer",
        "Tester",
    ]
    assert result.final_decision == "ready_for_human_approval"


def test_reviewer_rework_routes_to_named_developer(
    project,
    monkeypatch,
):
    routing = Routing(
        task="Refactor the addition behavior without changing its contract.",
        project=str(project),
        intent="refactor",
        risk="medium",
        lane="Fast Lane",
        quality_profile="standard",
        recipe="refactor",
        starting_role="Developer",
        workflow="Developer -> Tester -> Reviewer -> Human",
    )
    monkeypatch.setattr(
        "agentcrew.orchestrator.classify",
        lambda *args, **kwargs: routing,
    )
    developer_submission = {
        "sender": "Developer",
        "receiver": "Tester",
        "decision": "ready_for_test",
        "next_action": "Tester validates the change.",
    }
    tester_submission = {
        "sender": "Tester",
        "receiver": "Reviewer",
        "decision": "ready_for_review",
        "next_action": "Reviewer inspects the diff.",
    }
    provider = MockProvider(
        scripts={
            "Developer": [
                ScriptedTurn(
                    tool_calls=[
                        {"name": "read_file", "input": {"path": "broken.py"}},
                        {
                            "name": "edit_file",
                            "input": {
                                "path": "broken.py",
                                "old_string": "return a - b",
                                "new_string": "return a + b",
                            },
                        },
                        {
                            "name": "bash",
                            "input": {
                                "command": "python3 -m py_compile broken.py"
                            },
                        },
                    ],
                    submission=developer_submission,
                ),
                ScriptedTurn(
                    tool_calls=[
                        {
                            "name": "edit_file",
                            "input": {
                                "path": "broken.py",
                                "old_string": "return a + b",
                                "new_string": "return a + b  # reviewed",
                            },
                        },
                        {
                            "name": "bash",
                            "input": {
                                "command": "python3 -m py_compile broken.py"
                            },
                        },
                    ],
                    submission=developer_submission,
                ),
            ],
            "Tester": [
                ScriptedTurn(
                    tool_calls=[
                        {
                            "name": "bash",
                            "input": {"command": "python3 -m unittest -q"},
                        }
                    ],
                    submission=tester_submission,
                ),
                ScriptedTurn(
                    tool_calls=[
                        {
                            "name": "bash",
                            "input": {"command": "python3 -m unittest -q"},
                        }
                    ],
                    submission=tester_submission,
                ),
            ],
            "Reviewer": [
                ScriptedTurn(
                    tool_calls=[
                        {
                            "name": "read_file",
                            "input": {"path": "broken.py"},
                        }
                    ],
                    submission={
                        "sender": "Reviewer",
                        "receiver": "Developer",
                        "decision": "rework_required",
                        "next_action": "Developer addresses the finding.",
                    },
                ),
                ScriptedTurn(
                    tool_calls=[
                        {
                            "name": "read_file",
                            "input": {"path": "broken.py"},
                        }
                    ],
                    submission={
                        "sender": "Reviewer",
                        "receiver": "Human",
                        "decision": "ready_for_human_approval",
                        "next_action": "Human reviews the evidence.",
                    },
                ),
            ],
        }
    )

    result = run_team(
        task="Refactor the addition behavior without changing its contract.",
        project_dir=project,
        root=find_agentcrew_root(),
        provider=provider,
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )

    assert [handoff.sender for handoff in result.handoffs] == [
        "Developer",
        "Tester",
        "Reviewer",
        "Developer",
        "Tester",
        "Reviewer",
    ]
    assert result.final_decision == "ready_for_human_approval"


def test_tester_content_mutation_of_dirty_file_is_detected(project):
    (project / "test_mutating.py").write_text(
        "import unittest\n"
        "from pathlib import Path\n\n"
        "class MutatingTest(unittest.TestCase):\n"
        "    def test_mutates_source(self):\n"
        "        path = Path('broken.py')\n"
        "        path.write_text(path.read_text() + '# tester mutation\\n')\n"
    )
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(
        ["git", "-C", str(project), "config", "user.name", "Test"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "add", "."],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "commit", "-qm", "baseline"],
        check=True,
    )

    result = run_team(
        task="Fix broken.py so add_numbers(a, b) returns a + b",
        project_dir=project,
        root=find_agentcrew_root(),
        provider=demo_provider(),
        model_for_role=_model_for_every_role(),
        routing_approver=auto_approve,
    )

    assert result.final_decision == "tester_modified_worktree"
    assert "# tester mutation" in (project / "broken.py").read_text()


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
