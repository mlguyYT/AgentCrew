"""--from-agent JSONL mode (P0 #2)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def project(tmp_path: Path) -> Path:
    p = tmp_path / "proj"
    p.mkdir()
    (p / "broken.py").write_text("def add_numbers(a, b):\n    return a - b\n")
    return p


def _run_cli(project: Path) -> list[dict]:
    """Run the CLI in --from-agent mode and parse the JSONL stream."""
    repo_root = Path(__file__).resolve().parent.parent
    env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "AGENTCREW_ROOT": str(repo_root.parent),
    }
    result = subprocess.run(
        [
            str(repo_root / ".venv/bin/agentcrew-engine"),
            "run",
            "--task", "Fix broken.py so add_numbers returns a + b",
            "--project", str(project),
            "--backend", "mock-demo",
            "--from-agent",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
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
