"""The public demo runs offline and leaves caller projects untouched."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from agentcrew.cli import main


ROOT = Path(__file__).resolve().parents[2]


def test_demo_runs_twice_from_an_unrelated_project(tmp_path):
    sentinel = tmp_path / "broken.py"
    sentinel.write_text("This is the user's application, not the demo fixture.\n")
    before = sentinel.read_bytes()
    for _ in range(2):
        result = subprocess.run(
            [ROOT / "bin" / "agentcrew", "demo"],
            cwd=tmp_path,
            env={**os.environ, "AGENTCREW_ROOT": str(ROOT)},
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, result.stderr
        assert "Lane: Fast Lane" in result.stdout
        assert "Lane: Full Lane" in result.stdout
        assert "CEO approval before: Developer" in result.stdout
        assert "python3 -m unittest -q: pass" in result.stdout
        assert "Final decision: ready_for_human_approval" in result.stdout
        assert "Model API calls: 0" in result.stdout
    assert sentinel.read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["broken.py"]


@pytest.mark.parametrize("backend", [[], ["--backend", "mock-demo"]])
@pytest.mark.parametrize("jsonl", [[], ["--from-agent"]])
def test_unsupported_run_explains_how_to_start_without_creating_state(tmp_path, capsys, backend, jsonl):
    result = main(["run", "--project", str(tmp_path), "--task", "Fix login validation", *backend, *jsonl])
    output = capsys.readouterr()
    assert result == 2
    if jsonl:
        event = json.loads(output.out)
        assert event["event"] == "error"
        assert "agentcrew demo" in event["message"]
    else:
        assert "agentcrew demo" in output.err
    assert not (tmp_path / ".agent-state").exists()


def test_explicit_mock_backend_is_not_replaced_by_project_backend(tmp_path, capsys):
    config_dir = tmp_path / ".agentcrew"
    config_dir.mkdir()
    (config_dir / "config.yaml").write_text("backend: openai\n")
    result = main(["run", "--project", str(tmp_path), "--task", "Fix login validation", "--backend", "mock-demo"])
    assert result == 2
    assert "bundled broken.py/test_broken.py fixture" in capsys.readouterr().err


def test_run_without_backend_uses_project_config(tmp_path, capsys):
    config_dir = tmp_path / ".agentcrew"
    config_dir.mkdir()
    (config_dir / "config.yaml").write_text("backend: mock-demo\n")
    result = main(["run", "--project", str(tmp_path), "--task", "Fix login validation"])
    assert result == 2
    assert "bundled broken.py/test_broken.py fixture" in capsys.readouterr().err


@pytest.mark.parametrize("jsonl", [[], ["--from-agent"]])
def test_exhausted_mock_script_returns_an_actionable_error(tmp_path, capsys, jsonl):
    (tmp_path / "broken.py").write_text("def add_numbers(a, b):\n    return a - b\n")
    (tmp_path / "test_broken.py").write_text(
        "import unittest\nclass Failing(unittest.TestCase):\n"
        "    def test_fixture(self): self.fail('Different task needs a real backend')\n"
    )
    result = main([
        "run", "--project", str(tmp_path), "--task",
        "Fix broken.py so add_numbers returns a + b", "--backend", "mock-demo",
        "--auto-approve-routing", *jsonl,
    ])
    output = capsys.readouterr()
    assert result == 2
    if jsonl:
        event = json.loads(output.out.splitlines()[-1])
        assert event["event"] == "error"
        assert "agentcrew demo" in event["message"]
    else:
        assert "Scripted demo could not complete" in output.err
    assert "Traceback" not in output.out + output.err
