"""Handoff schema mirrors protocols/handoff-format.md. If this drifts,
the engine stops being a faithful executor of the methodology."""

import pytest
from pydantic import ValidationError

from agentcrew.handoff import Handoff, submit_handoff_input_schema


def _h(**overrides):
    base = dict(
        sender="Developer",
        receiver="Tester",
        decision="ready_for_test",
        next_action="run tests",
    )
    return Handoff(**{**base, **overrides})


def test_minimal_handoff_validates():
    h = _h()
    assert h.sender == "Developer"
    assert h.receiver == "Tester"
    assert h.context == []
    assert h.evidence == []


def test_context_capped_at_three():
    # the methodology says: 1–3 bullets only.
    with pytest.raises(ValidationError):
        _h(context=["a", "b", "c", "d"])


def test_open_questions_capped_at_five():
    with pytest.raises(ValidationError):
        _h(open_questions=["q1", "q2", "q3", "q4", "q5", "q6"])


def test_render_markdown_matches_v1_shape():
    md = _h(
        context=["Fast Lane task.", "Unit test command ran."],
        decision="Rework required.",
        evidence=["pytest failed.", "Got plain text, expected JSON."],
        next_action="Return JSON body and rerun.",
        open_questions=[],
    ).render_markdown()
    # Header
    assert md.startswith("## Developer -> Tester Handoff")
    # All five required sections present and in the methodology's order
    for needle in (
        "### Context",
        "### Decision",
        "### Evidence",
        "### Next Action",
        "### Open Questions",
    ):
        assert needle in md
    # Open Questions empty renders as "None." per the methodology's example
    assert "None." in md


def test_optional_sections_only_appear_when_used():
    md = _h(acceptance_criteria=["criterion A"]).render_markdown()
    assert "### Acceptance Criteria" in md
    assert "criterion A" in md

    md2 = _h().render_markdown()
    assert "### Acceptance Criteria" not in md2  # not added by default
    assert "### Validation" not in md2


def test_validation_limitation_renders_when_declared():
    md = _h(
        validation_status="unavailable",
        validation_limitation="Project has no test runner configured.",
    ).render_markdown()
    assert "### Validation" in md
    assert "- status: unavailable" in md
    assert "Project has no test runner configured." in md


def test_unavailable_validation_requires_a_limitation():
    with pytest.raises(ValidationError):
        _h(validation_status="unavailable")


def test_submit_handoff_schema_pins_sender_and_receivers():
    schema = submit_handoff_input_schema("Reviewer", ["Developer", "Tester", "Human"])
    assert schema["properties"]["sender"]["enum"] == ["Reviewer"]
    assert set(schema["properties"]["receiver"]["enum"]) == {"Developer", "Tester", "Human"}
    assert set(schema["required"]) == {"sender", "receiver", "decision", "next_action"}
