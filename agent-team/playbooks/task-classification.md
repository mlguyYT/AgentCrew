# Task Classification Playbook

## Purpose

This playbook helps agents decide which workflow lane to use.

The goal is to keep simple work fast and risky work safe.

---

## Risk levels

```yaml
risk_levels:
  low:
    lane: Fast Lane
    review_required: optional

  medium:
    lane: Fast Lane or Full Lane
    review_required: usually

  high:
    lane: Full Lane
    review_required: required

  critical:
    lane: Full Lane plus human decision
    review_required: required
```

---

## Low-risk tasks

Use Fast Lane.

Examples:

```yaml
low_risk_examples:
  - documentation update
  - small bug fix
  - minor UI text change
  - simple unit test
  - small isolated endpoint
  - simple internal tool change
```

Recommended flow:

```text
Developer -> Tester -> Human
```

---

## Medium-risk tasks

Use Fast Lane with Reviewer, or Full Lane if unclear.

Examples:

```yaml
medium_risk_examples:
  - new feature in existing area
  - API behavior change
  - non-critical database read change
  - moderate refactor
  - user-facing UI behavior
```

Recommended flow:

```text
Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human
```

---

## High-risk tasks

Use Full Lane.

Examples:

```yaml
high_risk_examples:
  - authentication
  - authorization
  - billing
  - data writes
  - migration
  - infrastructure
  - CI/CD
  - deployment
  - public API change
```

Recommended flow:

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human
```

---

## Critical-risk tasks

Use Full Lane with explicit human decision.

Examples:

```yaml
critical_risk_examples:
  - deleting data
  - changing payment flow
  - changing permission model
  - rotating production secrets
  - destructive infrastructure operations
  - major architecture replacement
```

Recommended flow:

```text
Advisor -> Idea Consultant -> Human decision -> Product Manager -> Human backlog approval -> Developer -> Tester -> Reviewer -> Specialist Reviewer -> Human
```

Specialist Reviewer means Security Reviewer, UX / Design Reviewer, or Documentation Agent when the task touches that area.

---

## Classification checklist

Before starting, answer:

```yaml
questions:
  - Does this touch auth?
  - Does this touch billing?
  - Does this touch customer data?
  - Does this require migration?
  - Does this affect production infrastructure?
  - Is rollback difficult?
  - Is the task vague?
  - Is the PR likely to be large?
  - Would a bug be expensive?
  - Does this need security, UX/design, or documentation specialist review?
```

If any answer is yes, consider Full Lane.

---

## Default request routing

Users do not need to choose the role or lane.

When a request does not name a role, classify it and route it:

```yaml
route_request:
  planning_or_idea: Advisor or Product Manager
  scoped_implementation: Developer
  validation_or_regression_check: Tester
  review_or_quality_check: Reviewer
  security_sensitive_change: Security Reviewer after normal review
  user_facing_flow_or_design: UX / Design Reviewer after normal review
  docs_or_examples_change: Documentation Agent when useful
  skill_change: Skill Validator
```

Then run the selected lane:

```text
Fast Lane: Developer -> Tester -> Reviewer if needed -> Human
Full Lane: Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human
```

If the user explicitly asks for a role, use that role unless risk requires escalation.

---

## Escalation rules

Escalate to Full Lane if:

```yaml
escalate_if:
  - risk becomes clearer during work
  - scope grows
  - unclear product decision appears
  - tests reveal broad regression risk
  - reviewer identifies architecture concern
```

---

## Default policy

When uncertain:

```text
Choose the safer lane or ask the human.
```

But do not over-escalate tiny work.

---

## Agent instruction

When classifying tasks:

```text
Prefer Fast Lane for small, reversible work.
Use Full Lane for risky, ambiguous, or high-impact work.
```
