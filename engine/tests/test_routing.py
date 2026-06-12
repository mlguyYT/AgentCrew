"""Routing parser tests — make sure we read the classifier script output faithfully."""

import pytest

from agentcrew.routing import Routing, _parse_yaml


SAMPLE = """\
task_classification:
  task: 'Fix the login form so empty email shows a validation message.'
  project: 'Team'
  intent: 'implementation_or_bug_fix'
  risk: 'low'
  lane: 'Fast Lane'
  quality_profile: 'standard'
  recipe: 'bug-fix'
  starting_role: 'Developer'
  workflow: 'Developer -> Tester -> Human'
  next_roles:
    - 'Tester'
    - 'Human'
  reviewers:
    - none
  specialists:
    - 'UX / Design Reviewer'
  skills:
    - none
  gates:
    - 'tester validation'
    - 'specialist routing check'
  human_decisions:
    - 'final approval before merge'
  files_to_load:
    - 'agent-team/context/route-index.md'
    - 'agent-team/agents/developer.md'
  reasons:
    - 'request asks for implementation'
  note: 'Heuristic classification.'
"""


def test_parses_scalars():
    r = _parse_yaml(SAMPLE)
    assert r.intent == "implementation_or_bug_fix"
    assert r.risk == "low"
    assert r.lane == "Fast Lane"
    assert r.recipe == "bug-fix"
    assert r.starting_role == "Developer"
    assert r.workflow == "Developer -> Tester -> Human"


def test_parses_lists():
    r = _parse_yaml(SAMPLE)
    assert r.next_roles == ["Tester", "Human"]
    assert r.specialists == ["UX / Design Reviewer"]
    assert r.gates == ["tester validation", "specialist routing check"]
    assert r.reviewers == []  # 'none' marker → empty
    assert r.skills == []
    assert r.reasons == ["request asks for implementation"]


def test_workflow_roles_extracted():
    r = _parse_yaml(SAMPLE)
    assert r.workflow_roles() == ["Developer", "Tester", "Human"]
    # Sample has UX / Design Reviewer as a specialist; it's auto-appended after
    # the primary workflow per specialist-review-routing.md.
    assert r.acting_roles_in_order() == ["Developer", "Tester", "UX / Design Reviewer"]


def test_conditional_role_skipped_when_condition_false():
    r = Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix",
        starting_role="Developer",
        workflow="Developer -> Tester -> Reviewer if risk is meaningful -> Human",
    )
    # risk='low' is not meaningful, so Reviewer is skipped.
    assert r.acting_roles_in_order() == ["Developer", "Tester"]


def test_conditional_role_included_when_condition_true():
    r = Routing(
        task="t", project="p", intent="i", risk="high", lane="Full Lane",
        quality_profile="strict", recipe="bug-fix",
        starting_role="Developer",
        workflow="Developer -> Tester -> Reviewer if risk is meaningful -> Human",
    )
    # risk='high' is meaningful, so Reviewer runs.
    assert r.acting_roles_in_order() == ["Developer", "Tester", "Reviewer"]


def test_specialist_reviewer_placeholder_expands():
    r = Routing(
        task="t", project="p", intent="i", risk="critical", lane="Full Lane plus explicit human decision",
        quality_profile="strict", recipe="release",
        starting_role="Advisor",
        workflow="Advisor -> Developer -> Tester -> Reviewer -> Specialist Reviewer -> Human",
        specialists=["Security Reviewer", "Release Manager"],
    )
    roles = r.acting_roles_in_order()
    assert roles == ["Advisor", "Developer", "Tester", "Reviewer", "Security Reviewer", "Release Manager"]


def test_specialist_reviewer_placeholder_skipped_when_no_specialists():
    r = Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix",
        starting_role="Reviewer",
        workflow="Reviewer -> Specialist Reviewer if needed -> Human",
        specialists=[],  # 'if needed' is false when there are none
    )
    assert r.acting_roles_in_order() == ["Reviewer"]


def test_specialists_not_in_workflow_are_appended():
    """Per specialist-review-routing.md, named specialists run even when
    the workflow string doesn't mention them."""
    r = Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix",
        starting_role="Developer",
        workflow="Developer -> Tester -> Human",
        specialists=["UX / Design Reviewer"],
    )
    assert r.acting_roles_in_order() == ["Developer", "Tester", "UX / Design Reviewer"]


def test_specialist_runs_once_when_in_workflow_and_specialists():
    """Don't double-add a role that's both in the workflow string AND specialists."""
    r = Routing(
        task="t", project="p", intent="i", risk="high", lane="Full Lane",
        quality_profile="strict", recipe="feature",
        starting_role="Developer",
        workflow="Developer -> Tester -> Security Reviewer -> Human",
        specialists=["Security Reviewer"],
    )
    roles = r.acting_roles_in_order()
    assert roles.count("Security Reviewer") == 1
    assert roles == ["Developer", "Tester", "Security Reviewer"]


def test_unknown_condition_defaults_to_include():
    """Conservative: if we can't evaluate the condition, run the role anyway."""
    r = Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix",
        starting_role="Documentation Agent",
        workflow="Documentation Agent -> Reviewer if behavior claims changed -> Human",
    )
    # 'behavior claims changed' isn't evaluable from routing alone → include.
    assert "Reviewer" in r.acting_roles_in_order()


def test_human_decision_is_an_event_not_a_role():
    """'Human decision' mid-workflow is a gate event, not an acting role."""
    r = Routing(
        task="t", project="p", intent="i", risk="critical",
        lane="Full Lane plus explicit human decision",
        quality_profile="strict", recipe="bug-fix",
        starting_role="Advisor",
        workflow="Advisor -> Idea Consultant -> Human decision -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer -> Human",
        specialists=["Security Reviewer"],
    )
    roles = r.acting_roles_in_order()
    assert "Human decision" not in roles
    assert "Human" not in roles
    assert roles == ["Advisor", "Idea Consultant", "Product Manager", "Developer", "Tester", "Reviewer", "Security Reviewer"]
    assert r.has_mid_workflow_human_gate() is True


def test_no_mid_workflow_human_gate_on_normal_route():
    r = Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix",
        starting_role="Developer",
        workflow="Developer -> Tester -> Human",
    )
    assert r.has_mid_workflow_human_gate() is False


def test_quoted_apostrophes_unescape():
    yaml = "task_classification:\n  task: 'apostrophe''s'\n  project: 'p'\n  intent: 'x'\n  risk: 'low'\n  lane: 'Fast Lane'\n  quality_profile: 'standard'\n  recipe: 'bug-fix'\n  starting_role: 'Developer'\n  workflow: 'Developer -> Tester -> Human'\n"
    r = _parse_yaml(yaml)
    assert r.task == "apostrophe's"


def test_missing_header_raises():
    with pytest.raises(ValueError, match="task_classification"):
        _parse_yaml("not the right shape\n")
