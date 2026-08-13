"""Team decisions continuity (.agent-state/decisions.md)."""

from pathlib import Path

from agentcrew.decisions import (
    load_recent,
    record_decision,
    render_section,
)


def test_record_creates_file_with_header(tmp_path):
    p = tmp_path / "decisions.md"
    record_decision(p, title="Use Postgres", decided_by=["PM"], rationale="Scaling.")
    text = p.read_text()
    assert "# Team Decisions" in text  # header initialized
    assert "Use Postgres" in text
    assert "Decided by: PM" in text
    assert "Rationale: Scaling." in text


def test_append_does_not_clobber(tmp_path):
    p = tmp_path / "decisions.md"
    record_decision(p, title="A", decided_by=["X"], rationale="r1")
    record_decision(p, title="B", decided_by=["Y"], rationale="r2")
    text = p.read_text()
    assert "A" in text
    assert "B" in text


def test_load_recent_limits(tmp_path):
    p = tmp_path / "decisions.md"
    for i in range(15):
        record_decision(p, title=f"D{i}", decided_by=["X"], rationale="r")
    recent = load_recent(p, limit=5)
    # Most recent 5 only
    assert "D14" in recent
    assert "D10" in recent
    assert "D9" not in recent


def test_load_recent_empty(tmp_path):
    assert load_recent(tmp_path / "missing.md") == ""


def test_render_section_blank_when_empty():
    assert render_section("") == ""


def test_render_section_wraps_with_label():
    text = "## 2026-05-28 · Use Postgres\nDecided by: PM"
    out = render_section(text)
    assert "Team decisions" in out
    assert "Use Postgres" in out


def test_run_with_id_recorded(tmp_path):
    p = tmp_path / "decisions.md"
    record_decision(p, title="X", decided_by=["PM"], rationale="r", run_id="20260528-100000-abc")
    text = p.read_text()
    assert "Run: 20260528-100000-abc" in text


# --- Orchestrator integration ----------------------------------------------


def test_decisions_section_appears_in_provider_user_message(tmp_path):
    """The orchestrator should inject the decisions section into role messages."""
    import json

    from agentcrew.demo_script import demo_provider
    from agentcrew.orchestrator import auto_approve, run as run_team
    from agentcrew.provider import MockProvider, ScriptedTurn
    from agentcrew.agentcrew_root import find_agentcrew_root

    project = tmp_path / "proj"
    project.mkdir()
    (project / "broken.py").write_text("def add_numbers(a, b): return a - b\n")
    (project / "test_broken.py").write_text(
        "import unittest\n"
        "from broken import add_numbers\n\n"
        "class AddNumbersTest(unittest.TestCase):\n"
        "    def test_adds(self):\n"
        "        self.assertEqual(add_numbers(2, 3), 5)\n"
    )
    (project / ".agent-state").mkdir()
    record_decision(
        project / ".agent-state" / "decisions.md",
        title="Use ' a + b ' style addition",
        decided_by=["Reviewer"],
        rationale="Team convention",
    )

    # Wrap demo provider to capture each role's user message
    base = demo_provider()
    captured: dict[str, str] = {}
    orig = base.run_agent

    def capturing_run(*, role, system_prompt, user_message, **kw):
        captured[role] = user_message
        return orig(role=role, system_prompt=system_prompt, user_message=user_message, **kw)

    base.run_agent = capturing_run

    root = find_agentcrew_root()
    result = run_team(
        task="Fix broken.py so add_numbers returns a + b",
        project_dir=project,
        root=root,
        provider=base,
        model_for_role={r: f"mock-{r}" for r in ("Developer", "Tester", "Reviewer")},
        routing_approver=auto_approve,
    )
    assert "Developer" in captured
    # The decisions section is injected into every role's user message
    assert "Team decisions" in captured["Developer"]
    assert "Use ' a + b ' style addition" in captured["Developer"]
