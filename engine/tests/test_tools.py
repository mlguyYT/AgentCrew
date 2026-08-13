"""Tool sandbox — using the methodology's role names.

Every tool-spec leak through this is a security regression.
"""

from pathlib import Path
import subprocess

import pytest

from agentcrew.tools import ToolError, build_tools
from agentcrew.role_runner import git_status_short


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "src.py").write_text("x = 1\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "deep.py").write_text("y = 2\n")
    return tmp_path


def _tool(specs, name):
    for s in specs:
        if s.name == name:
            return s
    raise KeyError(name)


# --- per-role allowlist (role names) ---


def test_developer_has_write(project):
    specs = build_tools("Developer", project)
    assert {s.name for s in specs} == {"read_file", "write_file", "edit_file", "bash"}


def test_tester_cannot_write(project):
    specs = build_tools("Tester", project)
    assert {s.name for s in specs} == {"read_file", "bash"}


def test_reviewer_is_read_only(project):
    specs = build_tools("Reviewer", project)
    assert {s.name for s in specs} == {
        "read_file",
        "grep",
        "glob",
        "git_diff",
    }


def test_reviewer_git_diff_reads_the_real_patch(project):
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(
        ["git", "-C", str(project), "add", "src.py"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(project),
            "-c",
            "user.name=AgentCrew Test",
            "-c",
            "user.email=agentcrew@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    (project / "src.py").write_text("x = 2\n")

    diff = _tool(build_tools("Reviewer", project), "git_diff")
    result = diff.handler()

    assert " M src.py" in result
    assert "-x = 1" in result
    assert "+x = 2" in result


def test_reviewer_git_diff_includes_untracked_file_content(project):
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    (project / "new.py").write_text("answer = 42\n")

    diff = _tool(build_tools("Reviewer", project), "git_diff")
    result = diff.handler()

    assert "?? new.py" in result
    assert "+answer = 42" in result
    assert str(project) not in result


def test_reviewer_git_diff_includes_staged_files_before_first_commit(project):
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(
        ["git", "-C", str(project), "add", "src.py"],
        check=True,
    )

    diff = _tool(build_tools("Reviewer", project), "git_diff")
    result = diff.handler()

    assert "A  src.py" in result
    assert "+x = 1" in result


def test_reviewer_default_diff_is_scoped_to_engine_observed_paths(project):
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(
        ["git", "-C", str(project), "add", "src.py", "sub/deep.py"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(project),
            "-c",
            "user.name=AgentCrew Test",
            "-c",
            "user.email=agentcrew@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    (project / "src.py").write_text("x = 2\n")
    (project / "sub" / "deep.py").write_text("y = 3\n")

    diff = _tool(
        build_tools(
            "Reviewer",
            project,
            review_paths=("src.py",),
        ),
        "git_diff",
    )
    result = diff.handler()

    assert "+x = 2" in result
    assert "deep.py" not in result


def test_git_status_is_scoped_to_nested_target_project(tmp_path):
    repository = tmp_path / "repository"
    project = repository / "project"
    project.mkdir(parents=True)
    (project / "app.py").write_text("value = 1\n")
    (repository / "sibling.py").write_text("value = 1\n")
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "add", "."],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=AgentCrew Test",
            "-c",
            "user.email=agentcrew@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    (project / "app.py").write_text("value = 2\n")
    (repository / "sibling.py").write_text("value = 2\n")

    status = git_status_short(project)

    assert status == " M app.py\n"


def test_reviewer_git_diff_rejects_path_escape(project):
    diff = _tool(build_tools("Reviewer", project), "git_diff")

    with pytest.raises(ToolError, match="escapes the project root"):
        diff.handler(paths=["../../../etc/passwd"])


def test_software_architect_is_read_only(project):
    specs = build_tools("Software Architect Agent", project)
    assert {s.name for s in specs} == {"read_file", "grep", "glob"}


def test_security_reviewer_is_read_only(project):
    specs = build_tools("Security Reviewer", project)
    assert {s.name for s in specs} == {"read_file", "grep", "glob"}


def test_ux_design_reviewer_is_read_only(project):
    specs = build_tools("UX / Design Reviewer", project)
    assert {s.name for s in specs} == {"read_file", "grep", "glob"}


def test_documentation_agent_can_write_docs_only(project):
    specs = build_tools("Documentation Agent", project)
    assert {"read_file", "grep", "glob", "write_file", "edit_file"}.issubset({s.name for s in specs})
    # but write_file is restricted to docs paths
    write = _tool(specs, "write_file")
    with pytest.raises(ToolError, match="only write to docs"):
        write.handler(path="src.py", content="# bad")


def test_documentation_agent_can_write_markdown(project):
    specs = build_tools("Documentation Agent", project)
    write = _tool(specs, "write_file")
    assert "wrote" in write.handler(path="docs/note.md", content="hi")


def test_unknown_v1_role_raises(project):
    with pytest.raises(ValueError, match="unknown role"):
        build_tools("HypeMaster", project)


def test_recommended_local_model_roles_are_real_agentcrew_roles():
    from agentcrew.agentcrew_root import AVAILABLE_ROLES
    from agentcrew.provider_local import recommended_models_for_code

    assert set(recommended_models_for_code()).issubset(set(AVAILABLE_ROLES))


# --- sandbox boundaries (unchanged from prior) ---


def test_read_refuses_path_traversal(project):
    specs = build_tools("Developer", project)
    read = _tool(specs, "read_file")
    with pytest.raises(ToolError, match="escapes the project root"):
        read.handler(path="../../../etc/passwd")


def test_bash_denylist_blocks_rm_rf(project):
    specs = build_tools("Developer", project)
    bash = _tool(specs, "bash")
    with pytest.raises(ToolError, match="denylist"):
        bash.handler(command="rm -rf /")


def test_bash_allowlist_blocks_unknown_binary(project):
    specs = build_tools("Developer", project)
    bash = _tool(specs, "bash")
    with pytest.raises(ToolError, match="allowlist"):
        bash.handler(command="nc -l 1234")


def test_bash_rejects_executable_paths_outside_project(project):
    bash = _tool(build_tools("Developer", project), "bash")

    with pytest.raises(ToolError, match="within the project root"):
        bash.handler(command="/tmp/python3 -m py_compile src.py")


def test_tester_blocks_arbitrary_python_execution(project):
    specs = build_tools("Tester", project)
    bash = _tool(specs, "bash")
    with pytest.raises(ToolError, match="Tester allowlist"):
        bash.handler(command="python3 -c 'open(\"src.py\", \"w\").write(\"bad\")'")
    assert (project / "src.py").read_text() == "x = 1\n"


def test_tester_allows_python_test_modules(project):
    (project / "test_src.py").write_text(
        "import unittest\n\n"
        "class SourceTest(unittest.TestCase):\n"
        "    def test_value(self):\n"
        "        self.assertEqual(1, 1)\n"
    )
    bash = _tool(build_tools("Tester", project), "bash")

    result = bash.handler(command="python3 -m unittest -q")

    assert "exit=0" in result


def test_bash_does_not_interpret_shell_redirection(project):
    specs = build_tools("Developer", project)
    bash = _tool(specs, "bash")
    result = bash.handler(command="echo changed > src.py")
    assert "exit=0" in result
    assert (project / "src.py").read_text() == "x = 1\n"


def test_edit_requires_unique_match(project):
    (project / "dup.py").write_text("a\na\n")
    specs = build_tools("Developer", project)
    edit = _tool(specs, "edit_file")
    with pytest.raises(ToolError, match="matches 2 times"):
        edit.handler(path="dup.py", old_string="a", new_string="b")
