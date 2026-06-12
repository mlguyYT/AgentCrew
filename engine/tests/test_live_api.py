"""Opt-in live-API integration tests.

These tests skip unless real API credentials are present in the environment.
They cost real tokens. They are intentionally NOT marked for CI by default;
to run them locally:

  OPENAI_API_KEY=...    pytest -v -m live_api tests/test_live_api.py
  ANTHROPIC_API_KEY=... pytest -v -m live_api tests/test_live_api.py

Why these tests exist: mocks lie. When provider SDKs change tool-call
shapes, when the classifier emits a new gate name, when our handoff
schema drifts — only a live run catches it.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from agentcrew.orchestrator import auto_approve, run as run_team
from agentcrew.agentcrew_root import find_agentcrew_root


# pytest marker; configured by pytest -m live_api or by a [tool.pytest.ini_options]
# markers entry. We don't add it to pyproject; we just register here.
def pytest_configure(config):  # pragma: no cover — only fires if pytest imports this
    config.addinivalue_line("markers", "live_api: tests that call real LLM providers")


@pytest.fixture
def live_project(tmp_path: Path) -> Path:
    """A tiny project for live-API runs. Kept minimal so token spend is small."""
    p = tmp_path / "live"
    p.mkdir()
    (p / "broken.py").write_text(
        "def add_numbers(a, b):\n"
        "    # Intentional bug for AgentCrew demo: subtraction where addition is meant.\n"
        "    return a - b\n"
    )
    (p / "README.md").write_text("# Live API demo\n")
    return p


@pytest.mark.live_api
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_openai_real_run_on_tiny_bug_fix(live_project):
    """End-to-end real run against OpenAI (default api.openai.com).

    To target a non-OpenAI endpoint, set OPENAI_BASE_URL.
    """
    from agentcrew.provider_openai import OpenAICompatibleProvider

    root = find_agentcrew_root()
    provider = OpenAICompatibleProvider()
    # Use the cheapest tool-capable OpenAI model so a CI test costs ~$0.01.
    model = os.environ.get("AGENTCREW_LIVE_OPENAI_MODEL", "gpt-4o-mini")
    result = run_team(
        task="Fix broken.py so add_numbers(a, b) returns a + b. Do not change anything else.",
        project_dir=live_project,
        root=root,
        provider=provider,
        model_for_role={
            "Developer": model,
            "Tester": model,
        },
        routing_approver=auto_approve,
    )
    assert result.handoffs
    assert "return a + b" in (live_project / "broken.py").read_text()
    assert result.next_owner == "human"
    assert result.actual_cost_usd > 0
    assert result.cost_estimate is not None


@pytest.mark.live_api
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
def test_anthropic_real_run_on_tiny_bug_fix(live_project):
    """End-to-end real run against the optional Anthropic backend.

    Expected outcome: the Developer agent reads broken.py, edits the
    operator, the Tester verifies, and the workflow terminates at human
    approval. Total spend should be well under $0.20.
    """
    from agentcrew.provider_anthropic import AnthropicProvider

    root = find_agentcrew_root()
    provider = AnthropicProvider()
    model = os.environ.get("AGENTCREW_LIVE_ANTHROPIC_MODEL", "claude-sonnet-4-6")
    result = run_team(
        task="Fix broken.py so add_numbers(a, b) returns a + b. Do not change anything else.",
        project_dir=live_project,
        root=root,
        provider=provider,
        model_for_role={
            "Developer": model,
            "Tester": model,
        },
        routing_approver=auto_approve,
    )
    assert result.handoffs, "Live run produced no handoffs"
    assert "return a + b" in (live_project / "broken.py").read_text()
    assert result.next_owner == "human"
    assert result.actual_cost_usd > 0
    assert result.cost_estimate is not None
