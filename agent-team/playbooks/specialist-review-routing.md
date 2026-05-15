# Specialist Review Routing

## Purpose

This playbook tells agents when to involve a specialist reviewer.

Specialist reviewers are used only when their area is touched. They do not replace Developer, Tester, Reviewer, or human approval.

---

## Routing Table

```yaml
security_reviewer:
  role_file: agent-team/agents/security-reviewer.md
  template: agent-team/templates/security-review-report.md
  triggers:
    - authentication
    - authorization
    - permissions
    - secrets
    - customer data
    - sensitive data
    - payments or billing
    - dependency changes
    - infrastructure permissions
    - public API exposure
    - input handling with injection risk

ux_design_reviewer:
  role_file: agent-team/agents/ux-design-reviewer.md
  template: agent-team/templates/ux-design-review-report.md
  triggers:
    - UI changes
    - user-facing flows
    - onboarding
    - forms
    - navigation
    - accessibility
    - responsive behavior
    - visual layout
    - copy that changes user understanding

documentation_agent:
  role_file: agent-team/agents/documentation-agent.md
  template: agent-team/templates/documentation-report.md
  triggers:
    - README changes
    - installation docs
    - usage docs
    - examples
    - changelog
    - release notes
    - public API behavior
    - migration notes

skill_validator:
  role_file: agent-team/agents/skill-validator.md
  template: agent-team/templates/skill-validation-report.md
  triggers:
    - new Skill added
    - Skill changed
    - Skill registry changed
    - Skill category reorganized
    - Skill trigger changed
```

---

## Fast Lane Use

In Fast Lane, add a specialist only when the trigger is directly present.

Example:

```text
Developer -> Tester -> Security Reviewer -> Human
```

Do not add specialist review for unrelated areas.

---

## Full Lane Use

In Full Lane, identify needed specialist review during Product Manager planning and confirm again after implementation.

Example:

```text
Product Manager -> Developer -> Tester -> Reviewer -> UX / Design Reviewer -> Human
```

If scope changes during implementation, rerun this routing check.

---

## Multiple Specialists

Use more than one specialist only when multiple areas are touched.

Example:

```text
Checkout redesign with payment copy:
  - Security Reviewer for payment/data risk
  - UX / Design Reviewer for checkout flow
  - Documentation Agent for release notes or usage docs
```

Keep reports separate so findings stay actionable.

---

## Non-Triggers

Do not involve a specialist only because:

- the role exists
- the PR is small but unrelated to the specialist area
- a reviewer has style preferences
- docs mention a feature but no docs behavior changed

---

## Handoff Rule

Specialist rework routes back to the original Developer unless the issue is docs-only and the Documentation Agent is explicitly assigned to update docs.

Human approval remains required.
