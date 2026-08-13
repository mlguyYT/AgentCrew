"""Trailing specialists run in parallel (#4)."""

import threading
import time
from pathlib import Path

import pytest

from agentcrew.orchestrator import (
    _split_trailing_specialists,
    auto_approve,
    run as run_team,
)
from agentcrew.provider import MockProvider, ScriptedTurn
from agentcrew.agentcrew_root import find_agentcrew_root


# --- Pure unit tests for the split ----------------------------------------


def test_split_no_specialists_returns_all_as_primary():
    primary, trailing = _split_trailing_specialists(["Developer", "Tester"], [])
    assert primary == ["Developer", "Tester"]
    assert trailing == []


def test_split_trailing_specialists_after_primary():
    primary, trailing = _split_trailing_specialists(
        ["Developer", "Tester", "Reviewer", "Security Reviewer", "UX / Design Reviewer"],
        ["Security Reviewer", "UX / Design Reviewer"],
    )
    assert primary == ["Developer", "Tester", "Reviewer"]
    assert trailing == ["Security Reviewer", "UX / Design Reviewer"]


def test_split_interleaved_specialist_stays_primary():
    """Specialist in the middle of the workflow is NOT parallelized."""
    primary, trailing = _split_trailing_specialists(
        ["Developer", "Security Reviewer", "Tester"],
        ["Security Reviewer"],
    )
    assert primary == ["Developer", "Security Reviewer", "Tester"]
    assert trailing == []


def test_split_all_specialists_at_end():
    primary, trailing = _split_trailing_specialists(
        ["Security Reviewer", "UX / Design Reviewer"],
        ["Security Reviewer", "UX / Design Reviewer"],
    )
    assert primary == []
    assert trailing == ["Security Reviewer", "UX / Design Reviewer"]


# --- Integration: trailing specialists actually run concurrently ----------


@pytest.fixture
def project(tmp_path: Path) -> Path:
    p = tmp_path / "proj"
    p.mkdir()
    (p / "broken.py").write_text(
        "def add_numbers(a, b):\n    return a - b\n"
    )
    (p / "test_broken.py").write_text(
        "import unittest\n"
        "from broken import add_numbers\n\n"
        "class AddNumbersTest(unittest.TestCase):\n"
        "    def test_adds(self):\n"
        "        self.assertEqual(add_numbers(2, 3), 5)\n"
    )
    return p


def _all_models() -> dict[str, str]:
    return {
        role: f"mock-{role}"
        for role in (
            "Advisor", "Idea Consultant", "Product Manager",
            "Developer", "Tester", "Reviewer",
            "Security Reviewer", "Release Manager",
            "UX / Design Reviewer", "Documentation Agent",
            "Researcher Agent", "Support Triage Agent", "LLM Agent",
            "CNN Agent", "Skill Validator",
        )
    }


def _accept_risk(_routing, _role) -> bool:
    return True


class _BlockingMock(MockProvider):
    """MockProvider that sleeps before submitting, so we can detect concurrency."""

    def __init__(self, scripts, sleep_seconds: float, started_event: threading.Event = None):
        super().__init__(scripts)
        self.sleep = sleep_seconds
        self.started_at: dict[str, float] = {}
        self.finished_at: dict[str, float] = {}
        self._lock = threading.Lock()

    def run_agent(self, *, role, **kwargs):
        with self._lock:
            self.started_at[role] = time.monotonic()
        time.sleep(self.sleep)
        run = super().run_agent(role=role, **kwargs)
        with self._lock:
            self.finished_at[role] = time.monotonic()
        return run


def _continue(sender: str, receiver: str = "Human") -> dict:
    """Non-terminal handoff so the orchestrator keeps walking the workflow."""
    return {
        "sender": sender,
        "receiver": receiver,
        "decision": "ready_for_next_role",
        "context": ["mock"],
        "evidence": ["mock"],
        "next_action": "next role acts",
        "open_questions": [],
    }


def _final(sender: str, receiver: str = "Human") -> dict:
    """Trailing-specialist handoff — terminal, human-gate decision."""
    return {
        "sender": sender,
        "receiver": receiver,
        "decision": "ready_for_human_approval",
        "context": ["mock"],
        "evidence": ["mock"],
        "next_action": "human approves",
        "open_questions": [],
    }


def _developer_turn() -> ScriptedTurn:
    return ScriptedTurn(
        tool_calls=[
            {"name": "read_file", "input": {"path": "broken.py"}},
            {
                "name": "edit_file",
                "input": {
                    "path": "broken.py",
                    "old_string": "return a - b",
                    "new_string": "return a + b",
                },
            },
            {
                "name": "bash",
                "input": {"command": "python3 -m py_compile broken.py"},
            },
        ],
        submission=_continue("Developer"),
    )


def _tester_turn() -> ScriptedTurn:
    return ScriptedTurn(
        tool_calls=[
            {
                "name": "bash",
                "input": {"command": "python3 -m unittest -q"},
            }
        ],
        submission=_continue("Tester"),
    )


def _reviewer_turn() -> ScriptedTurn:
    return ScriptedTurn(
        tool_calls=[
            {"name": "read_file", "input": {"path": "broken.py"}}
        ],
        submission=_continue("Reviewer"),
    )


def test_trailing_specialists_run_concurrently(project):
    """Two trailing specialists should run in overlapping time windows."""
    root = find_agentcrew_root()

    SLEEP = 0.3
    # Primary roles return non-terminal so the loop walks. Trailing specialists
    # return the terminal human-approval decision.
    primary = ("Advisor", "Idea Consultant", "Product Manager", "Developer", "Tester", "Reviewer")
    trailing = ("Security Reviewer", "Release Manager")
    scripts = {role: [ScriptedTurn(submission=_continue(role))] for role in primary}
    scripts["Developer"] = [_developer_turn()]
    scripts["Tester"] = [_tester_turn()]
    scripts["Reviewer"] = [_reviewer_turn()]
    scripts.update({role: [ScriptedTurn(submission=_final(role))] for role in trailing})
    provider = _BlockingMock(scripts=scripts, sleep_seconds=SLEEP)

    result = run_team(
        task="Rotate the production secret in deploy config",
        project_dir=project,
        root=root,
        provider=provider,
        model_for_role=_all_models(),
        routing_approver=auto_approve,
        risk_acceptor=_accept_risk,
    )

    # Sanity: the run got to specialists at all.
    senders = {h.sender for h in result.handoffs}
    assert "Security Reviewer" in senders
    assert "Release Manager" in senders

    # Were the trailing specialists overlapping in time?
    started = provider.started_at
    finished = provider.finished_at
    # Both specialists must have started, and one must have started while the other
    # was still running.
    s_start = started["Security Reviewer"]
    r_start = started["Release Manager"]
    s_finish = finished["Security Reviewer"]
    r_finish = finished["Release Manager"]
    overlap_start = max(s_start, r_start)
    overlap_end = min(s_finish, r_finish)
    assert overlap_end > overlap_start, (
        f"trailing specialists were not concurrent: SR started={s_start}, "
        f"finished={s_finish}; RM started={r_start}, finished={r_finish}"
    )


def test_specialists_persisted_in_deterministic_order(project):
    """Handoffs are stored in input order even if threads finish in any order."""
    root = find_agentcrew_root()
    primary = ("Advisor", "Idea Consultant", "Product Manager", "Developer", "Tester", "Reviewer")
    trailing = ("Security Reviewer", "Release Manager")
    scripts = {role: [ScriptedTurn(submission=_continue(role))] for role in primary}
    scripts["Developer"] = [_developer_turn()]
    scripts["Tester"] = [_tester_turn()]
    scripts["Reviewer"] = [_reviewer_turn()]
    scripts.update({role: [ScriptedTurn(submission=_final(role))] for role in trailing})
    provider = _BlockingMock(scripts=scripts, sleep_seconds=0.05)

    result = run_team(
        task="Rotate the production secret in deploy config",
        project_dir=project,
        root=root,
        provider=provider,
        model_for_role=_all_models(),
        routing_approver=auto_approve,
        risk_acceptor=_accept_risk,
    )

    # The acting order from routing is Release Manager before Security Reviewer
    # (per the classifier output we verified earlier). Confirm the engine preserved
    # that input order, not a "first thread to finish" order.
    senders = [h.sender for h in result.handoffs]
    assert senders[-2:] == ["Release Manager", "Security Reviewer"]


def test_low_risk_run_is_unaffected(project):
    """Low-risk tasks have no trailing specialists → no parallelism, no regression."""
    from agentcrew.demo_script import demo_provider

    root = find_agentcrew_root()
    result = run_team(
        task="Fix broken.py so add_numbers returns a + b",
        project_dir=project,
        root=root,
        provider=demo_provider(),
        model_for_role=_all_models(),
        routing_approver=auto_approve,
    )
    assert result.final_decision == "ready_for_human_approval"
    senders = [h.sender for h in result.handoffs]
    assert senders == ["Developer", "Tester"]
