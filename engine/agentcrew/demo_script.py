"""Bundled mock demo: scripts a Developer + Tester run for the toy example.

Uses the deterministic classifier (no mocking that — it's deterministic) and
mocks only the LLM calls per role. Demonstrates the engine: the
real classifier picks Developer → Tester → Human for the brief, and our
scripted mocks fulfill those roles.
"""

from __future__ import annotations

from .provider import MockProvider, ScriptedTurn


def demo_provider() -> MockProvider:
    return MockProvider(
        scripts={
            "Advisor": [
                ScriptedTurn(
                    tool_calls=[],
                    submission={
                        "answer": (
                            "For a coding-team dashboard, default to **Server-Sent Events** "
                            "unless you genuinely need bidirectional traffic.\n\n"
                            "Why: SSE is HTTP, replays cleanly through proxies, has built-in "
                            "reconnect with `Last-Event-ID`, and the server-to-client direction "
                            "covers 'live status updates' fully. Websockets add complexity "
                            "(framing, ping/pong, separate auth) you only need for chat or "
                            "collaborative editing."
                        ),
                    },
                ),
            ],
            "Developer": [
                ScriptedTurn(
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
                        {"name": "bash", "input": {"command": "python3 -m py_compile broken.py"}},
                    ],
                    submission={
                        "sender": "Developer",
                        "receiver": "Tester",
                        "decision": "Patched the operator; ready for test.",
                        "context": [
                            "broken.py used `-` where the brief says `+`.",
                            "No other call sites; change is local.",
                        ],
                        "evidence": [
                            "broken.py:2 — replaced `return a - b` with `return a + b`.",
                            "`python3 -m py_compile broken.py` exit 0.",
                        ],
                        "files": ["broken.py"],
                        "next_action": "Run the test_broken.py assertions against the patched file.",
                        "open_questions": [],
                    },
                ),
            ],
            "Tester": [
                ScriptedTurn(
                    tool_calls=[
                        {"name": "read_file", "input": {"path": "broken.py"}},
                        {
                            "name": "bash",
                            "input": {
                                "command": "python3 -m unittest -q"
                            },
                        },
                    ],
                    submission={
                        "sender": "Tester",
                        "receiver": "Human",
                        "decision": "ready_for_human_approval",
                        "context": ["Ran the project regression tests against patched broken.py."],
                        "evidence": [
                            "`python3 -m unittest -q` exited 0.",
                            "The project regression tests passed.",
                        ],
                        "commands": ["python3 -m unittest -q: pass"],
                        "next_action": "Human approves and merges.",
                        "open_questions": [],
                    },
                ),
            ],
        }
    )
