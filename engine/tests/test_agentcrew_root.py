"""Tests for agentcrew.agentcrew_root — the single place that resolves
where the AgentCrew installation lives, mapping role names to file paths.
"""

from pathlib import Path

import pytest

from agentcrew.agentcrew_root import _role_slug, find_agentcrew_root


def test_role_slug_simple():
    assert _role_slug("Developer") == "developer"


def test_role_slug_two_words():
    assert _role_slug("Security Reviewer") == "security-reviewer"


def test_role_slug_slash():
    assert _role_slug("UX / Design Reviewer") == "ux-design-reviewer"


def test_role_slug_three_words():
    assert _role_slug("Support Triage Agent") == "support-triage-agent"


def test_find_agentcrew_root_finds_sibling():
    # engine/ sits one level under the AgentCrew root, so the parent of this
    # checkout should be a valid AgentCrew installation.
    root = find_agentcrew_root()
    assert (root.path / "AGENTS.md").exists()
    assert (root.path / "agent-team").is_dir()
    assert root.classifier.exists()


def test_find_agentcrew_root_fails_useful_message_when_explicit_path_bogus(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not look like an AgentCrew install"):
        find_agentcrew_root(explicit=tmp_path)


def test_role_file_resolves_for_real_role():
    root = find_agentcrew_root()
    p = root.role_file("Developer")
    assert p.exists()
    assert p.name == "developer.md"


def test_role_file_raises_for_unknown_role():
    root = find_agentcrew_root()
    with pytest.raises(FileNotFoundError):
        root.role_file("Imaginary Role")


def test_methodology_file_blocks_path_traversal():
    root = find_agentcrew_root()
    with pytest.raises(ValueError, match="must be relative"):
        root.methodology_file("../etc/passwd")
    with pytest.raises(ValueError, match="must be relative"):
        root.methodology_file("/etc/passwd")
