"""--from-agent JSONL mode (P0 #2)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from agentcrew.continuation import write_continuation
from agentcrew.handoff import Handoff
from agentcrew.routing import Routing


@pytest.fixture
def project(tmp_path: Path) -> Path:
    p = tmp_path / "proj"
    p.mkdir()
    (p / "broken.py").write_text("def add_numbers(a, b):\n    return a - b\n")
    (p / "test_broken.py").write_text(
        "import unittest\n"
        "from broken import add_numbers\n\n"
        "class AddNumbersTest(unittest.TestCase):\n"
        "    def test_adds(self):\n"
        "        self.assertEqual(add_numbers(2, 3), 5)\n"
    )
    return p


def _run_cli(
    project: Path,
    *,
    task: str = "Fix broken.py so add_numbers returns a + b",
    extra_env: dict | None = None,
    extra_args: list[str] | None = None,
    expected_returncode: int = 0,
) -> list[dict]:
    """Run the CLI in --from-agent mode and parse the JSONL stream."""
    repo_root = Path(__file__).resolve().parent.parent
    env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "AGENTCREW_ROOT": str(repo_root.parent),
    }
    if extra_env:
        env.update(extra_env)
    command = [
        sys.executable,
        "-m",
        "agentcrew.cli",
        "run",
        "--task",
        task,
        "--project",
        str(project),
        "--backend",
        "mock-demo",
        "--from-agent",
    ]
    command.extend(extra_args or [])
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == expected_returncode, f"CLI failed: {result.stderr}\nstdout={result.stdout}"
    events = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        events.append(json.loads(line))
    return events


def test_emits_routing_event_first(project):
    events = _run_cli(project)
    assert events[0]["event"] == "routing"
    assert events[0]["lane"] == "Fast Lane"
    assert events[0]["recipe"] == "bug-fix"
    assert events[0]["acting_roles"] == ["Developer", "Tester"]


def test_emits_role_lifecycle_events(project):
    events = _run_cli(project)
    types = [e["event"] for e in events]
    # role_started and role_finished come in pairs for each acting role.
    assert types.count("role_started") == 2
    assert types.count("role_finished") == 2
    # Order: routing → routing_approved → role_started/finished × N → done
    assert types[0] == "routing"
    assert types[1] == "routing_approved"
    assert types[-1] == "done"


def test_done_event_carries_run_dir_and_handoffs(project):
    events = _run_cli(project)
    done = [e for e in events if e["event"] == "done"][0]
    assert done["final_decision"] == "ready_for_human_approval"
    assert done["next_owner"] == "human"
    assert Path(done["run_dir"]).exists()
    assert len(done["handoffs"]) == 2
    assert done["handoffs"][0]["sender"] == "Developer"


def test_every_event_has_event_and_ts(project):
    events = _run_cli(project)
    for ev in events:
        assert "event" in ev
        assert "ts" in ev
        assert isinstance(ev["ts"], (int, float))


def test_from_agent_stops_for_cost_approval_when_model_has_price(project):
    events = _run_cli(
        project,
        extra_env={"AGENTCREW_MODEL": "gpt-4o-mini"},
        expected_returncode=1,
    )
    types = [e["event"] for e in events]
    assert "cost_preview" in types
    assert types[-1] == "cost_approval_required"
    assert "role_started" not in types


def test_from_agent_continues_after_explicit_cost_approval(project):
    events = _run_cli(
        project,
        extra_env={"AGENTCREW_MODEL": "gpt-4o-mini"},
        extra_args=["--approve-cost"],
    )

    types = [event["event"] for event in events]
    assert "cost_approval_required" not in types
    assert types.count("role_started") == 2
    assert types[-1] == "done"
    preview = next(event for event in events if event["event"] == "cost_preview")
    assert preview["estimated_total_usd"] == events[-1]["estimated_cost_usd"]


def test_from_agent_resumes_after_ceo_gate_without_repeating_planning(project):
    run_id = "planning_run"
    run_dir = project / ".agent-state" / "runs" / run_id
    run_dir.mkdir(parents=True)
    routing = Routing(
        task="Fix broken.py so add_numbers returns a + b",
        project=project.name,
        intent="idea_to_product_delivery",
        risk="low",
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
    planning = Handoff(
        sender="Product Manager",
        receiver="Human",
        decision="needs_human_decision",
        context=["The plan is ready."],
        next_action="CEO approves execution.",
    )
    write_continuation(run_dir, routing=routing, handoffs=[planning])

    events = _run_cli(
        project,
        extra_args=["--continue-run", run_id, "--approve-decision"],
    )

    assert events[0]["acting_roles"] == ["Developer", "Tester"]
    assert "Advisor" not in [
        event.get("role")
        for event in events
        if event["event"] == "role_started"
    ]
    done = events[-1]
    assert [handoff["sender"] for handoff in done["handoffs"]] == [
        "Product Manager",
        "Developer",
        "Tester",
    ]
    assert "approved: approve product direction" in (
        project / ".agent-state" / "human-decisions.md"
    ).read_text()

    replay_events = _run_cli(
        project,
        extra_args=["--continue-run", run_id, "--approve-decision"],
        expected_returncode=2,
    )
    assert replay_events == []


def test_product_idea_runs_planning_then_emits_continuation(project):
    events = _run_cli(
        project,
        task="I want to build a scheduling app for clinics",
    )

    started = [
        event["role"] for event in events if event["event"] == "role_started"
    ]
    assert started == ["Advisor", "Idea Consultant", "Product Manager"]
    assert "Developer" not in started
    continuation = next(
        event for event in events if event["event"] == "continuation_ready"
    )
    assert continuation["next_role"] == "Developer"
    assert (Path(events[-1]["run_dir"]) / "continuation.json").is_file()

    resumed = _run_cli(
        project,
        extra_args=[
            "--continue-run",
            continuation["run_id"],
            "--approve-decision",
        ],
    )
    resumed_roles = [
        event["role"]
        for event in resumed
        if event["event"] == "role_started"
    ]
    assert resumed_roles == ["Developer", "Tester", "Reviewer"]
    assert resumed[-1]["final_decision"] == "ready_for_human_approval"
