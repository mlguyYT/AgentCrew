"""Real-repository regressions for host-side Git inspection."""

import hashlib
import os
from pathlib import Path
import shlex
import subprocess
import sys

import pytest

from agentcrew.git_inspection import (
    GitInspectionError,
    GitWorktreeSnapshot,
    capture_git_worktree_snapshot,
    list_git_changed_paths,
    read_git_diff,
)
from agentcrew.git_safety import git_command
from agentcrew.role_runner import git_status_short


def _fixture_git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(
        ["git", "-C", str(project), *args],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture(params=["committed", "unborn"])
def hostile_repository(tmp_path: Path, request):
    project = tmp_path / "project"
    project.mkdir()
    _fixture_git(project, "init", "-q")
    (project / ".gitattributes").write_text("*.txt diff=unsafe filter=unsafe\n")
    (project / "tracked.txt").write_text("tracked before\n")
    _fixture_git(project, "add", ".")
    if request.param == "committed":
        _fixture_git(
            project, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "fixture",
        )
    # Equal-sized edits also exercise Git's content checks and clean filters.
    (project / "tracked.txt").write_text("tracked after!\n")
    (project / "new.txt").write_text("untracked content\n")

    helper = tmp_path / "helper.py"
    helper.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        "Path(sys.argv[1]).write_text('executed outside project')\n"
        "print('helper output')\n"
    )
    markers = []
    for key in (
        "diff.unsafe.textconv", "diff.unsafe.command", "diff.external",
        "core.fsmonitor", "filter.unsafe.clean", "filter.unsafe.process",
    ):
        marker = tmp_path / (key + ".marker")
        markers.append(marker)
        command = shlex.join([sys.executable, str(helper), str(marker)])
        _fixture_git(project, "config", key, command)
    _fixture_git(project, "config", "filter.unsafe.required", "true")
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    hook_marker = tmp_path / "hook.marker"
    markers.append(hook_marker)
    hook = hooks / "post-index-change"
    hook.write_text(
        "#!/bin/sh\n" + shlex.join([sys.executable, str(helper), str(hook_marker)]) + "\n"
    )
    hook.chmod(0o755)
    _fixture_git(project, "config", "core.hooksPath", str(hooks))
    return project, markers, request.param


@pytest.mark.parametrize("inspection", ["diff", "paths", "snapshot", "short_status"])
def test_inspection_never_executes_repository_helpers(hostile_repository, inspection):
    project, markers, state = hostile_repository
    config_before = (project / ".git/config").read_bytes()
    index_before = (project / ".git/index").read_bytes()
    codes = {"tracked.txt": " M", "new.txt": "??"}
    if state == "unborn":
        codes = {".gitattributes": "A ", "tracked.txt": "AM", "new.txt": "??"}

    if inspection == "diff":
        result = read_git_diff(project, [])
        assert "+tracked after!" in result
        assert "+untracked content" in result
        assert "helper output" not in result
    elif inspection == "paths":
        assert list_git_changed_paths(project) == tuple(codes)
    elif inspection == "short_status":
        assert git_status_short(project) == "".join(
            f"{code} {path}\n" for path, code in codes.items()
        )
    else:
        expected = GitWorktreeSnapshot(tuple(
            (
                code,
                path,
                "file:" + hashlib.sha256((project / path).read_bytes()).hexdigest(),
            )
            for path, code in codes.items()
        ))
        assert capture_git_worktree_snapshot(project) == expected

    assert [marker.name for marker in markers if marker.exists()] == []
    assert (project / ".git/config").read_bytes() == config_before
    assert (project / ".git/index").read_bytes() == index_before


@pytest.mark.parametrize("source", ["repository", "config", "helpers", "trace"])
def test_git_environment_cannot_redirect_or_execute(hostile_repository, monkeypatch, source):
    project, markers, _ = hostile_repository
    outside = project.parent
    marker = outside / "injected.marker"
    helper_command = shlex.join([sys.executable, str(outside / "helper.py"), str(marker)])
    other = outside / "other"
    other.mkdir()
    _fixture_git(other, "init", "-q")
    (other / "outside.txt").write_text("must not inspect this repository\n")
    config = outside / "injected.config"
    config.write_text('[core]\n\tfsmonitor = ' + helper_command + '\n')

    injections = {
        "repository": {
            "GIT_DIR": str(other / ".git"),
            "GIT_WORK_TREE": str(other),
            "GIT_INDEX_FILE": str(other / ".git/index"),
            "GIT_COMMON_DIR": str(other / ".git"),
            "GIT_OBJECT_DIRECTORY": str(other / ".git/objects"),
        },
        "config": {
            "GIT_CONFIG": str(config),
            "GIT_CONFIG_GLOBAL": str(config),
            "GIT_CONFIG_SYSTEM": str(config),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.fsmonitor",
            "GIT_CONFIG_VALUE_0": helper_command,
            "GIT_CONFIG_PARAMETERS": shlex.quote("core.fsmonitor=" + helper_command),
        },
        "helpers": {"GIT_EXTERNAL_DIFF": helper_command, "GIT_PAGER": helper_command},
        "trace": {"GIT_TRACE": str(marker), "GIT_TRACE2_EVENT": str(marker)},
    }
    for key, value in injections[source].items():
        monkeypatch.setenv(key, value)

    result = read_git_diff(project, [])

    assert "+tracked after!" in result
    assert "+untracked content" in result
    assert "outside.txt" not in result
    assert not marker.exists()
    assert [path.name for path in markers if path.exists()] == []


def test_nested_project_inspection_remains_scoped(hostile_repository):
    project, markers, _ = hostile_repository
    nested = project / "nested"
    nested.mkdir()
    (nested / "local.txt").write_text("nested content\n")

    result = read_git_diff(nested, [])

    assert "+nested content" in result
    assert "tracked.txt" not in result
    assert "new.txt" not in result
    assert [path.name for path in markers if path.exists()] == []


def test_inspection_without_a_repository(tmp_path):
    assert list_git_changed_paths(tmp_path) is None
    assert capture_git_worktree_snapshot(tmp_path) is None
    with pytest.raises(GitInspectionError, match="git status is unavailable"):
        read_git_diff(tmp_path, [])


@pytest.mark.parametrize("text", [True, False])
def test_invalid_config_fails_closed(tmp_path, text):
    _fixture_git(tmp_path, "init", "-q")
    (tmp_path / ".git/config").write_text("[invalid\n")

    result = git_command(tmp_path, "status", "--short", "--", ".", text=text)

    assert result.returncode != 0
    assert isinstance(result.stdout, str if text else bytes)
    assert isinstance(result.stderr, str if text else bytes)


def test_git_helper_rejects_other_commands(tmp_path):
    with pytest.raises(ValueError, match="Only status, diff and ls-files"):
        git_command(tmp_path, "config", "core.fsmonitor", "unsafe")


def test_git_helper_drops_all_inherited_git_variables(tmp_path, monkeypatch):
    _fixture_git(tmp_path, "init", "-q")
    calls = []
    run = subprocess.run

    def record_run(*args, **kwargs):
        calls.append(kwargs["env"])
        return run(*args, **kwargs)

    monkeypatch.setenv("GIT_EXEC_PATH", str(tmp_path))
    monkeypatch.setenv("GIT_FUTURE_UNSAFE_SETTING", "untrusted")
    monkeypatch.setenv("git_future_unsafe_setting", "untrusted")
    monkeypatch.setattr("agentcrew.git_safety.subprocess.run", record_run)

    result = git_command(tmp_path, "ls-files", "--", ".")

    assert result.returncode == 0
    assert len(calls) == 2
    for env in calls:
        assert "GIT_EXEC_PATH" not in env
        assert "GIT_FUTURE_UNSAFE_SETTING" not in env
        assert "git_future_unsafe_setting" not in env


def test_status_does_not_execute_submodule_filters(hostile_repository):
    project, _, _ = hostile_repository
    submodule = project / "submodule"
    submodule.mkdir()
    _fixture_git(submodule, "init", "-q")
    (submodule / ".gitattributes").write_text("*.txt filter=submodule-unsafe\n")
    (submodule / "file.txt").write_text("before\n")
    _fixture_git(submodule, "add", ".")
    _fixture_git(
        submodule, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-qm", "fixture",
    )
    _fixture_git(
        project, "-c", "core.fsmonitor=false", "-c", f"core.hooksPath={os.devnull}",
        "-c", "filter.unsafe.clean=", "-c", "filter.unsafe.process=",
        "-c", "filter.unsafe.required=false", "add", "submodule",
    )
    # Configure this filter only in the nested repository, not its parent.
    marker = project.parent / "submodule-filter.marker"
    helper = shlex.join([sys.executable, str(project.parent / "helper.py"), str(marker)])
    _fixture_git(submodule, "config", "filter.submodule-unsafe.clean", helper)
    _fixture_git(submodule, "config", "filter.submodule-unsafe.required", "true")
    (submodule / "file.txt").write_text("after!\n")
    result = git_command(project, "status", "--short", "--", ".")

    assert result.returncode == 0
    assert "Am submodule\n" in result.stdout
    assert "Subproject commit" in read_git_diff(project, ["submodule"])
    assert not marker.exists()
