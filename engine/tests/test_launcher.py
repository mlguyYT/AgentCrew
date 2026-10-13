import os
import subprocess
from pathlib import Path


def _launcher() -> Path:
    return Path(__file__).resolve().parents[2] / "bin" / "agentcrew"


def _isolated_env(tmp_path: Path) -> dict[str, str]:
    return {
        **os.environ,
        "HOME": str(tmp_path),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "CODEX_HOME": str(tmp_path / "codex"),
    }


def test_loader_renders_private_ceo_profile_path(tmp_path: Path):
    result = subprocess.run(
        [_launcher(), "loader", "--root", str(_launcher().parents[1])],
        capture_output=True,
        text=True,
        env=_isolated_env(tmp_path),
        check=False,
    )

    profile = tmp_path / "config" / "agentcrew" / "ceo-profile.md"
    assert result.returncode == 0
    assert result.stderr == ""
    assert f"`{profile}`" in result.stdout


def test_install_creates_private_profile_without_overwriting_it(tmp_path: Path):
    command = [
        _launcher(),
        "install",
        "--agent",
        "codex",
        "--root",
        str(_launcher().parents[1]),
    ]
    env = _isolated_env(tmp_path)

    first = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    profile = tmp_path / "config" / "agentcrew" / "ceo-profile.md"
    profile.write_text("# My private preferences\n")
    second = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert first.returncode == 0
    assert second.returncode == 0
    assert profile.read_text() == "# My private preferences\n"
    assert "Preserved:" in second.stdout
    assert f"`{profile}`" in (tmp_path / "codex" / "AGENTS.md").read_text()


def test_context_manifest_loads_idea_to_product_contract(tmp_path: Path):
    result = subprocess.run(
        [
            _launcher(),
            "context",
            "--root",
            str(_launcher().parents[1]),
            "--project",
            str(tmp_path),
            "--task",
            "I want to build an AI scheduling app for clinics",
        ],
        capture_output=True,
        text=True,
        env=_isolated_env(tmp_path),
        check=False,
    )

    assert result.returncode == 0
    assert "agent-team/context/ceo-operating-context.md" in result.stdout
    assert "agent-team/policies/ceo-operating-contract.md" in result.stdout
    assert "agent-team/playbooks/idea-to-product.md" in result.stdout
    assert "agent-team/agents/idea-consultant.md" in result.stdout
    assert "agent-team/templates/executive-brief.md" in result.stdout
