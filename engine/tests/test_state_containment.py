"""Reject project-state aliases before any model call or external file write."""

import os

import pytest

from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew.audit import collect
from agentcrew.cli import main
from agentcrew.orchestrator import run
from agentcrew.provider import MockProvider
from agentcrew.routing import Routing
from agentcrew.show import find_latest_run
from agentcrew.state import build_layout, write_current_task
from agentcrew.state_paths import UnsafeStatePath
from agentcrew.git_inspection import capture_git_worktree_snapshot, list_git_changed_paths
import subprocess


@pytest.mark.parametrize("relative", ["", "runs", "current-task.md", "budget-history.jsonl", "decisions.md"])
def test_existing_state_alias_is_rejected_before_work(tmp_path, relative):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    if relative:
        (project / ".agent-state").mkdir()
    link = project / ".agent-state" / relative if relative else project / ".agent-state"
    link.symlink_to(outside, target_is_directory=True)
    provider = MockProvider({})
    routing = Routing(task="Review the plan", project=str(project), intent="review", risk="low",
                      lane="Fast Lane", quality_profile="standard", recipe="review",
                      starting_role="Product Manager", workflow="Product Manager -> Human")
    with pytest.raises(UnsafeStatePath):
        run(task=routing.task, project_dir=project, root=find_agentcrew_root(), provider=provider,
            model_for_role={"Product Manager": "mock"}, routing_override=routing)
    assert list(outside.iterdir()) == []


def test_hardlinked_state_file_cannot_overwrite_other_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    state = project / ".agent-state"
    state.mkdir()
    outside = tmp_path / "other-project-task.md"
    outside.write_text("Other project's task")
    os.link(outside, state / "current-task.md")
    with pytest.raises(UnsafeStatePath, match="hard-linked"):
        build_layout(project)
    assert outside.read_text() == "Other project's task"


def test_state_alias_created_after_layout_is_rejected_on_write(tmp_path):
    layout = build_layout(tmp_path)
    layout.state_dir.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("Preserved")
    layout.current_task.symlink_to(outside)
    routing = Routing("task", str(tmp_path), "review", "low", "Fast Lane", "standard", "review", "Product Manager", "Product Manager -> Human")
    with pytest.raises(UnsafeStatePath):
        write_current_task(layout, task="New task", routing=routing, owner="Product Manager")
    assert outside.read_text() == "Preserved"


def test_cli_and_readers_refuse_external_state_without_tracebacks(tmp_path, capsys):
    outside = tmp_path / "outside"
    outside.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    (project / ".agent-state").symlink_to(outside)
    assert main(["run", "--project", str(project), "--task", "Review plan", "--backend", "mock-demo", "--from-agent"]) == 2
    assert '"event":"error"' in capsys.readouterr().out
    for reader in (collect, find_latest_run):
        with pytest.raises(UnsafeStatePath):
            reader(project)
    assert list(outside.iterdir()) == []


def test_nested_project_snapshots_fingerprint_target_files(tmp_path):
    project = tmp_path / "nested"
    project.mkdir()
    source = project / "app.py"
    source.write_text("first version\n")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    assert list_git_changed_paths(project) == ("app.py",)
    before = capture_git_worktree_snapshot(project)
    source.write_text("second version\n")
    after = capture_git_worktree_snapshot(project)
    assert before != after
    assert before.entries[0][2].startswith("file:")
