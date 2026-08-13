"""Project-level config (.agentcrew/config.yaml) — P0 #3."""

from pathlib import Path

import pytest

from agentcrew.config import ProjectConfig


def _write(project: Path, body: str) -> None:
    (project / ".agentcrew").mkdir(parents=True, exist_ok=True)
    (project / ".agentcrew" / "config.yaml").write_text(body)


def _write_bug_test(project: Path) -> None:
    (project / "test_broken.py").write_text(
        "import unittest\n"
        "from broken import add_numbers\n\n"
        "class AddNumbersTest(unittest.TestCase):\n"
        "    def test_adds(self):\n"
        "        self.assertEqual(add_numbers(2, 3), 5)\n"
    )


@pytest.fixture
def project(tmp_path: Path) -> Path:
    return tmp_path / "proj"


def test_missing_config_returns_none(project):
    project.mkdir()
    assert ProjectConfig.load(project) is None


def test_minimal_valid_config(project):
    project.mkdir()
    _write(project, "quality_profile: strict\n")
    cfg = ProjectConfig.load(project)
    assert cfg is not None
    assert cfg.quality_profile == "strict"
    assert cfg.required_specialists == []
    assert cfg.models == {}


def test_invalid_profile_silently_dropped(project):
    project.mkdir()
    _write(project, "quality_profile: extreme-rigor-9000\n")
    cfg = ProjectConfig.load(project)
    assert cfg.quality_profile is None


def test_recipe_profiles(project):
    project.mkdir()
    _write(
        project,
        "recipe_profiles:\n"
        "  feature: strict\n"
        "  bug-fix: standard\n",
    )
    cfg = ProjectConfig.load(project)
    assert cfg.recipe_profiles == {"feature": "strict", "bug-fix": "standard"}
    assert cfg.profile_for_recipe("feature", "light") == "strict"
    assert cfg.profile_for_recipe("docs-update", "light") == "light"  # fallback


def test_global_profile_overrides_fallback(project):
    project.mkdir()
    _write(project, "quality_profile: regulated\n")
    cfg = ProjectConfig.load(project)
    assert cfg.profile_for_recipe("anything", "light") == "regulated"


def test_required_specialists_by_path_glob(project):
    project.mkdir()
    (project / "src").mkdir()
    (project / "src" / "auth").mkdir()
    (project / "src" / "auth" / "middleware.py").write_text("# auth\n")
    (project / "src" / "frontend").mkdir()
    (project / "src" / "frontend" / "app.tsx").write_text("// ui\n")

    _write(
        project,
        "required_specialists:\n"
        "  - paths: ['src/auth/**']\n"
        "    roles: ['Security Reviewer']\n"
        "  - paths: ['src/payments/**']\n"
        "    roles: ['Security Reviewer']\n",
    )
    cfg = ProjectConfig.load(project)
    # Only the auth rule matches (no src/payments/ exists)
    assert cfg.required_specialists_for_project(project) == ["Security Reviewer"]


def test_required_specialists_deduped(project):
    project.mkdir()
    (project / "src").mkdir()
    (project / "src" / "auth.py").write_text("# auth\n")
    (project / "src" / "payments.py").write_text("# pay\n")
    _write(
        project,
        "required_specialists:\n"
        "  - paths: ['src/auth*']\n"
        "    roles: ['Security Reviewer', 'UX / Design Reviewer']\n"
        "  - paths: ['src/payments*']\n"
        "    roles: ['Security Reviewer']\n",
    )
    cfg = ProjectConfig.load(project)
    out = cfg.required_specialists_for_project(project)
    assert out.count("Security Reviewer") == 1


def test_required_specialists_ignore_generated_and_state_dirs(project):
    project.mkdir()
    (project / ".agent-state" / "runs").mkdir(parents=True)
    (project / ".agent-state" / "runs" / "auth.py").write_text("# generated state\n")
    (project / "node_modules" / "pkg").mkdir(parents=True)
    (project / "node_modules" / "pkg" / "auth.py").write_text("# vendor\n")
    _write(
        project,
        "required_specialists:\n"
        "  - paths: ['**/auth.py']\n"
        "    roles: ['Security Reviewer']\n",
    )
    cfg = ProjectConfig.load(project)
    assert cfg.required_specialists_for_project(project) == []


def test_models_loaded(project):
    project.mkdir()
    _write(
        project,
        "models:\n"
        "  Developer: claude-sonnet-4-6\n"
        "  Reviewer: claude-opus-4-7\n",
    )
    cfg = ProjectConfig.load(project)
    assert cfg.models == {"Developer": "claude-sonnet-4-6", "Reviewer": "claude-opus-4-7"}


def test_backend_loaded(project):
    project.mkdir()
    _write(project, "backend: local\n")
    cfg = ProjectConfig.load(project)
    assert cfg.backend == "local"


def test_budget_defaults_and_overrides(project):
    project.mkdir()
    _write(
        project,
        "budget:\n"
        "  daily_max_usd: 10\n"
        "  per_run_warn_usd: 0.25\n",
    )
    cfg = ProjectConfig.load(project)
    assert cfg.budget.daily_max_usd == 10.0
    assert cfg.budget.per_run_warn_usd == 0.25
    assert cfg.budget.per_run_block_usd == 5.0  # default


def test_malformed_yaml_doesnt_crash(project):
    """A typo'd YAML key should still let the runtime start."""
    project.mkdir()
    _write(
        project,
        "qualityprofile: strict\n"  # typo
        "models:\n"
        "  Developer: claude-sonnet-4-6\n",
    )
    cfg = ProjectConfig.load(project)
    assert cfg.quality_profile is None  # typo silently dropped
    assert cfg.models == {"Developer": "claude-sonnet-4-6"}  # other keys still parsed


# --- Orchestrator integration -------------------------------------------------


def test_orchestrator_applies_recipe_profile_override(tmp_path):
    """A bug-fix → strict override in config should change the persisted profile."""
    from agentcrew.demo_script import demo_provider
    from agentcrew.orchestrator import auto_approve, run as run_team
    from agentcrew.agentcrew_root import find_agentcrew_root

    project = tmp_path / "proj"
    project.mkdir()
    (project / "broken.py").write_text("def add_numbers(a, b): return a - b\n")
    _write_bug_test(project)
    _write(
        project,
        "recipe_profiles:\n"
        "  bug-fix: strict\n",
    )

    root = find_agentcrew_root()
    result = run_team(
        task="Fix broken.py so add_numbers returns a + b",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role={r: f"mock-{r}" for r in (
            "Developer", "Tester", "Reviewer",
            "Security Reviewer", "UX / Design Reviewer",
        )},
        routing_approver=auto_approve,
    )
    # The classifier would normally pick 'standard' for this bug-fix.
    # The config overrides it to 'strict'.
    assert result.routing.quality_profile == "strict"
    # Reason logged
    assert any("profile" in r.lower() and "strict" in r.lower() for r in result.routing.reasons)


def test_orchestrator_adds_path_required_specialist(tmp_path):
    """If config requires Security Reviewer for auth paths AND auth files exist,
    Security Reviewer must run."""
    from agentcrew.demo_script import demo_provider
    from agentcrew.orchestrator import auto_approve, run as run_team
    from agentcrew.provider import MockProvider, ScriptedTurn
    from agentcrew.agentcrew_root import find_agentcrew_root

    project = tmp_path / "proj"
    project.mkdir()
    (project / "src").mkdir()
    (project / "src" / "auth.py").write_text("# auth\n")
    (project / "broken.py").write_text("def add_numbers(a, b): return a - b\n")
    _write_bug_test(project)
    _write(
        project,
        "required_specialists:\n"
        "  - paths: ['src/auth*']\n"
        "    roles: ['Security Reviewer']\n",
    )

    # We need a Security Reviewer script too — extend the demo provider.
    base = demo_provider()
    base._scripts["Security Reviewer"] = [
        ScriptedTurn(
            submission={
                "sender": "Security Reviewer",
                "receiver": "Human",
                "decision": "ready_for_human_approval",
                "context": ["reviewed for sec sensitivity"],
                "evidence": ["no auth code touched"],
                "next_action": "human approves",
                "open_questions": [],
            }
        )
    ]
    root = find_agentcrew_root()
    result = run_team(
        task="Fix broken.py so add_numbers returns a + b",
        project_dir=project,
        root=root,
        provider=base,
        model_for_role={r: f"mock-{r}" for r in (
            "Developer", "Tester", "Reviewer", "Security Reviewer",
            "UX / Design Reviewer",
        )},
        routing_approver=auto_approve,
    )
    senders = {h.sender for h in result.handoffs}
    assert "Security Reviewer" in senders  # added by config rule
    assert "Security Reviewer" in result.routing.specialists
