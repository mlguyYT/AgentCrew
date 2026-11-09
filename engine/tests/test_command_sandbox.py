"""Model-issued commands cannot reach host files, metadata, or networking."""

import shlex
import socket
from pathlib import Path

import pytest

from agentcrew import command_sandbox
from agentcrew.tools import ToolError, build_tools


def bash(project, command):
    tool = next(tool for tool in build_tools("Developer", project) if tool.name == "bash")
    return tool.handler(command=command)


def test_commands_cannot_read_or_write_outside_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    private = tmp_path / "private.txt"
    private.write_text("outside-project sentinel")
    result = bash(project, f"cat {shlex.quote(str(private))}")
    assert result.startswith("exit=1")
    assert "outside-project sentinel" not in result
    code = f"from pathlib import Path; Path({str(private)!r}).write_text('overwritten')"
    result = bash(project, "python3 -c " + shlex.quote(code))
    # This path exists only in the sandbox's private /tmp, not on the host.
    assert result.startswith("exit=0")
    assert private.read_text() == "outside-project sentinel"
    assert bash(project, "python3 -c \"from pathlib import Path; Path('local.txt').write_text('allowed')\"").startswith("exit=0")
    assert (project / "local.txt").read_text() == "allowed"


def test_commands_cannot_rewrite_git_or_engine_state(tmp_path):
    for name in (".git", ".agent-state", ".agentcrew"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "guard.txt").write_text("protected")
        code = f"from pathlib import Path; Path({str(directory / 'guard.txt')!r}).write_text('forged')"
        assert bash(tmp_path, "python3 -c " + shlex.quote(code)).startswith("exit=1")
        assert (directory / "guard.txt").read_text() == "protected"


def test_command_network_is_separate_from_host(tmp_path):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        code = f"import socket; socket.create_connection(('127.0.0.1', {port}), timeout=1)"
        result = bash(tmp_path, "python3 -c " + shlex.quote(code))
    assert result.startswith("exit=1")


def test_recursive_search_and_glob_do_not_follow_outside_symlinks(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    private = tmp_path / "private.txt"
    private.write_text("outside-project sentinel")
    (project / "link.txt").symlink_to(private)
    (project / "local.txt").write_text("local sentinel")
    tools = {tool.name: tool for tool in build_tools("Reviewer", project)}
    assert tools["grep"].handler(pattern="sentinel") == "local.txt:1: local sentinel"
    assert tools["glob"].handler(pattern="*.txt") == "local.txt"


def test_missing_sandbox_has_no_unconfined_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(command_sandbox.shutil, "which", lambda _: None)
    calls = []
    monkeypatch.setattr("agentcrew.tools.subprocess.run", lambda *a, **k: calls.append(a))
    with pytest.raises(ToolError, match="Unconfined execution is disabled"):
        bash(tmp_path, "true")
    assert calls == []


@pytest.mark.parametrize("path", [".git/config", ".agent-state/human-decisions.md", ".agentcrew/config.yaml"])
def test_file_tools_cannot_bypass_protected_metadata(tmp_path, path):
    target = tmp_path / path
    target.parent.mkdir()
    target.write_text("protected")
    tools = {tool.name: tool for tool in build_tools("Developer", tmp_path)}
    with pytest.raises(ToolError, match="metadata"):
        tools["write_file"].handler(path=path, content="forged")
    with pytest.raises(ToolError, match="metadata"):
        tools["edit_file"].handler(path=path, old_string="protected", new_string="forged")
    assert target.read_text() == "protected"


def test_documentation_scope_is_checked_after_normalizing_path(tmp_path):
    tools = {tool.name: tool for tool in build_tools("Documentation Agent", tmp_path)}
    with pytest.raises(ToolError, match="only write to docs"):
        tools["write_file"].handler(path="docs/../app.py", content="unrelated source change")
    assert not (tmp_path / "app.py").exists()
