from pathlib import Path

from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew.ceo_context import (
    MAX_CEO_CONTEXT_CHARS,
    context_for_routing,
    default_ceo_profile_path,
    load_ceo_context,
)
from agentcrew.role_runner import build_user_message
from agentcrew.routing import Routing


def test_default_profile_uses_xdg_config_home(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("AGENTCREW_CEO_PROFILE", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert default_ceo_profile_path() == tmp_path / "agentcrew" / "ceo-profile.md"


def test_explicit_profile_path_wins(monkeypatch, tmp_path: Path):
    selected = tmp_path / "private-profile.md"
    monkeypatch.setenv("AGENTCREW_CEO_PROFILE", str(selected))

    assert default_ceo_profile_path() == selected


def test_unmodified_template_is_not_injected(tmp_path: Path):
    root = find_agentcrew_root()
    profile = tmp_path / "ceo-profile.md"
    profile.write_text(
        root.methodology_file("agent-team/templates/ceo-profile.md").read_text()
    )

    context = load_ceo_context(root, profile_path=profile)

    assert context.profile_loaded is False
    assert "CEO operating contract" in context.text
    assert "preferred stacks:" not in context.text


def test_custom_profile_is_bounded_and_injected_without_its_path(tmp_path: Path):
    root = find_agentcrew_root()
    profile = tmp_path / "ceo-profile.md"
    profile.write_text(
        "# CEO Profile\n\n## Technical Preferences\n\n"
        "- Prefer Python services.\n"
        + ("x" * 2_000)
    )

    context = load_ceo_context(root, profile_path=profile)

    assert context.profile_loaded is True
    assert len(context.text) <= MAX_CEO_CONTEXT_CHARS
    assert "Prefer Python services" in context.text
    assert str(profile) not in context.text


def test_role_message_tells_team_to_handle_internal_coordination():
    root = find_agentcrew_root()
    context = load_ceo_context(root, profile_path=Path("/missing/profile"))
    routing = Routing(
        task="Build a product from this idea",
        project="example",
        intent="idea_to_product_delivery",
        risk="medium",
        lane="Full Lane",
        quality_profile="standard",
        recipe="feature",
        starting_role="Advisor",
        workflow="Advisor -> Product Manager -> Human decision -> Developer -> Human",
    )

    message = build_user_message(
        routing,
        [],
        "Advisor",
        ceo_context=context.text,
    )

    assert "Never ask the CEO to choose an internal role" in message
    assert "You are the **Advisor**" in message


def test_small_low_risk_task_skips_extra_ceo_context():
    root = find_agentcrew_root()
    routing = Routing(
        task="Fix a typo",
        project="example",
        intent="implementation_or_bug_fix",
        risk="low",
        lane="Fast Lane",
        quality_profile="standard",
        recipe="bug-fix",
        starting_role="Developer",
        workflow="Developer -> Tester -> Human",
    )

    context = context_for_routing(root, routing)

    assert context.text == ""
    assert context.profile_loaded is False
