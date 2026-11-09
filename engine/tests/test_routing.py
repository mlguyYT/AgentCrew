"""Routing parser tests — make sure we read the classifier script output faithfully."""

import pytest

from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew.routing import Routing, _parse_yaml, classify


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


def test_explicit_repeated_role_runs_twice():
    """An explicit later role is a separate workflow phase, not duplication."""
    r = Routing(
        task="t", project="p", intent="architecture_design_or_decision",
        risk="high", lane="Full Lane", quality_profile="strict",
        recipe="review", starting_role="Software Architect Agent",
        workflow=(
            "Software Architect Agent -> Developer -> Reviewer -> "
            "Software Architect Agent -> Human"
        ),
        specialists=["Software Architect Agent"],
    )
    assert r.acting_roles_in_order() == [
        "Software Architect Agent",
        "Developer",
        "Reviewer",
        "Software Architect Agent",
    ]


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


def test_named_human_approval_is_an_enforced_gate_not_a_role():
    r = Routing(
        task="t",
        project="p",
        intent="portfolio_project_positioning",
        risk="medium",
        lane="Full Lane",
        quality_profile="standard",
        recipe="portfolio-project",
        starting_role="Product Manager",
        workflow=(
            "Product Manager -> Human scope approval -> Developer -> "
            "Tester -> Human"
        ),
    )

    assert r.acting_roles_in_order() == ["Product Manager", "Developer", "Tester"]
    assert r.has_mid_workflow_human_gate() is True
    assert r.role_after_mid_workflow_human_gate() == "Developer"


def test_no_mid_workflow_human_gate_on_normal_route():
    r = Routing(
        task="t", project="p", intent="i", risk="low", lane="Fast Lane",
        quality_profile="standard", recipe="bug-fix",
        starting_role="Developer",
        workflow="Developer -> Tester -> Human",
    )
    assert r.has_mid_workflow_human_gate() is False


def test_real_classifier_routes_architecture_decision():
    root = find_agentcrew_root()
    r = classify(
        root,
        "Design service boundaries and data ownership for the billing subsystem",
        str(root.path),
    )
    assert r.intent == "architecture_design_or_decision"
    assert r.risk == "high"
    assert r.lane == "Full Lane"
    assert r.starting_role == "Software Architect Agent"
    assert r.acting_roles_in_order() == [
        "Software Architect Agent",
        "Product Manager",
        "Security Reviewer",
    ]
    assert "Software Architect Agent" in r.specialists
    assert "software-architecture" in r.skills
    assert "architecture decision gate" in r.gates
    assert "agent-team/playbooks/architecture-decisions.md" in r.files_to_load


def test_product_idea_with_delivery_plans_before_implementation():
    root = find_agentcrew_root()
    r = classify(
        root,
        "I want to build a product that helps freelancers manage proposals",
        str(root.path),
    )

    assert r.intent == "idea_to_product_delivery"
    assert r.starting_role == "Advisor"
    assert r.lane == "Full Lane"
    assert r.has_mid_workflow_human_gate() is True
    assert r.role_after_mid_workflow_human_gate() == "Developer"
    assert r.acting_roles_in_order() == [
        "Advisor",
        "Idea Consultant",
        "Product Manager",
        "Developer",
        "Tester",
        "Reviewer",
    ]
    assert any("execution boundary" in item for item in r.human_decisions)
    assert "agent-team/playbooks/idea-to-product.md" in r.files_to_load
    assert "agent-team/templates/executive-brief.md" in r.files_to_load


def test_critical_product_gate_includes_scope_and_risk_decisions():
    root = find_agentcrew_root()
    r = classify(
        root,
        "I want to build a product to change the payment flow",
        str(root.path),
    )

    decision = r.next_human_decision()
    assert "product direction" in decision
    assert "critical risk" in decision


def test_product_idea_question_stays_in_discovery():
    root = find_agentcrew_root()
    r = classify(
        root,
        "Should I build a scheduling app for independent designers?",
        str(root.path),
    )

    assert r.intent == "rough_idea_or_strategy"
    assert r.starting_role == "Advisor"
    assert r.lane == "Full Lane"
    assert r.has_mid_workflow_human_gate() is False
    assert r.acting_roles_in_order() == [
        "Advisor",
        "Idea Consultant",
        "Product Manager",
    ]


def test_scoped_build_request_still_starts_with_developer():
    root = find_agentcrew_root()
    r = classify(
        root,
        "Build a parser for the existing import format",
        str(root.path),
    )

    assert r.intent == "implementation_or_bug_fix"
    assert r.starting_role == "Developer"


def test_architecture_delivery_pauses_before_implementation():
    root = find_agentcrew_root()
    r = classify(
        root,
        "Implement a new service boundary and data ownership model for billing",
        str(root.path),
    )
    assert r.starting_role == "Software Architect Agent"
    assert r.has_mid_workflow_human_gate() is True
    assert r.role_after_mid_workflow_human_gate() == "Developer"
    assert r.acting_roles_in_order() == [
        "Software Architect Agent",
        "Product Manager",
        "Developer",
        "Tester",
        "Reviewer",
        "Software Architect Agent",
        "Security Reviewer",
    ]


def test_login_does_not_trigger_artifact_classification():
    root = find_agentcrew_root()
    r = classify(
        root,
        "Fix the login form so empty email shows a validation message",
        str(root.path),
    )
    assert "artifact classification check" not in r.gates


@pytest.mark.parametrize(
    ("task", "expected_roles"),
    [
        ("Prepare the release checklist", ["Release Manager", "Tester"]),
        (
            "Prepare release notes",
            ["Release Manager", "Tester", "Documentation Agent"],
        ),
        ("Prepare cloud readiness", ["Release Manager", "Tester"]),
        (
            "Triage this customer report",
            ["Support Triage Agent"],
        ),
        (
            "Refresh the documentation for the parser",
            ["Documentation Agent", "Tester", "Reviewer"],
        ),
        ("Tune the LLM prompt", ["LLM Agent"]),
        ("Tune CNN image classification", ["CNN Agent"]),
        ("Migrate the RAG embeddings", ["LLM Agent", "Developer", "Tester"]),
        ("Migrate the CNN inference routine", ["CNN Agent", "Developer", "Tester"]),
        (
            "Set public/private product wording",
            ["Product Manager", "Documentation Agent", "Security Reviewer"],
        ),
    ],
)
def test_classified_workflows_have_concrete_actor_sequences(task, expected_roles):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.acting_roles_in_order() == expected_roles
    assert r.next_roles == r.workflow_roles()[1:]
    for role in r.acting_roles_in_order():
        assert root.role_file(role).is_file()


@pytest.mark.parametrize(
    "task",
    [
        "Fix the parser for empty input",
        "Validate the parser",
        "Review the parser",
        "Research parser options",
        "Scope a portfolio project with authentication",
        "Triage a customer report about authentication",
        "Prepare cloud authentication checks",
        "Validate a new skill",
        "Build a parser with a behavior change",
        "Refresh documentation about authentication",
    ],
)
def test_classified_acting_roles_resolve_to_role_files(task):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.acting_roles_in_order()
    for role in r.acting_roles_in_order():
        assert root.role_file(role).is_file()
    # Even conditionally skipped steps must name real actors, not prose labels.
    for step in [*r.workflow_roles(), *r.next_roles]:
        role = step.partition(" if ")[0]
        if not role.startswith("Human") and role != "Specialist Reviewer":
            assert root.role_file(role).is_file()


@pytest.mark.parametrize(
    "task",
    [
        "Review destructive cleanup",
        "Validate destructive cleanup",
        "Research destructive cleanup options",
        "Scope a portfolio project with destructive cleanup",
        "Design a destructive service boundary",
        "Implement a destructive service boundary",
        "Fix destructive cleanup",
        "I want to build a product with destructive cleanup",
    ],
)
def test_critical_escalations_use_real_advisor_and_preserve_human_gate(task):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.risk == "critical"
    assert r.requires_human_decision_on_routing()
    assert r.has_mid_workflow_human_gate()
    assert "Advisor" in r.acting_roles_in_order()
    assert r.next_roles == r.workflow_roles()[1:]
    for role in r.acting_roles_in_order():
        assert root.role_file(role).is_file()
    for step in [*r.workflow_roles(), *r.next_roles]:
        role = step.partition(" if ")[0]
        if not role.startswith("Human") and role != "Specialist Reviewer":
            assert root.role_file(role).is_file()


@pytest.mark.parametrize(
    "task",
    [
        "Triage this customer report",
        "Triage this customer report: expected behavior, no defect",
        "Triage this customer report: a confirmed defect with reproduction steps",
        "Triage this customer report and assess a possible fix",
        "Triage this customer report: do not implement a fix",
        "Triage this customer report: the customer asks us to fix the parser",
        "Triage this customer report:\nFix the parser, says the customer",
        "Please triage this customer report",
    ],
)
def test_triage_only_does_not_schedule_delivery(task):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.intent == "support_triage_or_customer_issue"
    assert r.starting_role == "Support Triage Agent"
    assert r.execution_steps() == ["Support Triage Agent", "Human"]
    assert r.next_roles == ["Human"]


@pytest.mark.parametrize(
    "task",
    [
        "Fix this customer report",
        "Please implement a fix for this customer report",
        "Triage and fix this customer report",
        "Fix the confirmed defect from this customer report with reproduction steps",
    ],
)
def test_explicit_support_fix_requires_product_approval(task):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.intent == "support_triage_or_customer_issue"
    assert r.starting_role == "Support Triage Agent"
    assert r.execution_steps() == [
        "Support Triage Agent",
        "Product Manager",
        "Human product approval",
        "Developer",
        "Tester",
        "Human",
    ]
    assert r.next_roles == r.workflow_roles()[1:]
    assert r.has_mid_workflow_human_gate()
    assert r.role_after_mid_workflow_human_gate() == "Developer"
    assert r.workflow_after_mid_workflow_human_gate() == (
        "Developer -> Tester -> Reviewer if risk is meaningful -> Human"
    )
    assert "approve defect evidence" in r.next_human_decision()


@pytest.mark.parametrize(
    ("task", "risk", "steps"),
    [
        (
            "Triage this customer report about a behavior change",
            "medium",
            ["Support Triage Agent", "Human"],
        ),
        (
            "Triage this customer report about authentication",
            "high",
            ["Support Triage Agent", "Advisor", "Security Reviewer", "Human"],
        ),
        (
            "Triage this customer report about data loss",
            "critical",
            ["Support Triage Agent", "Advisor", "Human decision", "Human"],
        ),
    ],
)
def test_triage_risk_escalation_does_not_authorize_delivery(task, risk, steps):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.risk == risk
    assert r.intent == "support_triage_or_customer_issue"
    assert r.starting_role == "Support Triage Agent"
    assert r.execution_steps() == steps
    assert r.next_roles == r.workflow_roles()[1:]
    if risk == "critical":
        assert r.requires_human_decision_on_routing()
        assert r.has_mid_workflow_human_gate()
        assert r.role_after_mid_workflow_human_gate() is None
        assert "critical risk" in r.next_human_decision()


@pytest.mark.parametrize(
    "task",
    [
        "Triage this customer report about cloud authentication",
        "Triage this customer report about a service boundary and a proposed fix",
        "Triage this customer report about cloud data loss",
    ],
)
def test_explicit_triage_takes_precedence_over_report_subject(task):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.intent == "support_triage_or_customer_issue"
    assert r.starting_role == "Support Triage Agent"
    assert r.execution_steps()[0] == "Support Triage Agent"
    assert not {"Product Manager", "Developer", "Tester"} & set(r.execution_steps())
    assert r.next_roles == r.workflow_roles()[1:]


@pytest.mark.parametrize(
    ("task", "risk"),
    [
        ("Fix this customer report about authentication", "high"),
        ("Fix this customer report about data loss", "critical"),
    ],
)
def test_escalated_support_fix_still_requires_product_approval(task, risk):
    root = find_agentcrew_root()
    r = classify(root, task, str(root.path))

    assert r.risk == risk
    assert r.starting_role == "Support Triage Agent"
    assert r.execution_steps() == [
        "Support Triage Agent",
        "Advisor",
        "Product Manager",
        "Human product approval",
        "Developer",
        "Tester",
        "Reviewer",
        *(["Security Reviewer"] if risk == "high" else []),
        "Human",
    ]
    assert r.has_mid_workflow_human_gate()
    assert r.role_after_mid_workflow_human_gate() == "Developer"
    if risk == "critical":
        assert r.requires_human_decision_on_routing()
        assert "critical risk" in r.next_human_decision()


def test_legacy_triage_conditions_cannot_infer_runtime_outcomes():
    r = Routing(
        task="Triage this customer report",
        project="p",
        intent="support_triage_or_customer_issue",
        risk="low",
        lane="Fast Lane",
        quality_profile="standard",
        recipe="bug-fix",
        starting_role="Support Triage Agent",
        workflow=(
            "Support Triage Agent -> "
            "Product Manager if expected behavior or priority is unclear -> "
            "Tester if reproduction is required -> "
            "Developer if defect is confirmed -> "
            "Tester if defect is confirmed -> "
            "Developer if some future triage outcome -> Human"
        ),
        specialists=["Support Triage Agent"],
    )

    assert r.execution_steps() == ["Support Triage Agent", "Human"]


def test_quoted_apostrophes_unescape():
    yaml = "task_classification:\n  task: 'apostrophe''s'\n  project: 'p'\n  intent: 'x'\n  risk: 'low'\n  lane: 'Fast Lane'\n  quality_profile: 'standard'\n  recipe: 'bug-fix'\n  starting_role: 'Developer'\n  workflow: 'Developer -> Tester -> Human'\n"
    r = _parse_yaml(yaml)
    assert r.task == "apostrophe's"


def test_missing_header_raises():
    with pytest.raises(ValueError, match="task_classification"):
        _parse_yaml("not the right shape\n")
