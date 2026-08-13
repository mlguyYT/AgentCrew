# Fast Lane Playbook

## Purpose

Fast Lane is the default development workflow.

It is designed for startup-style execution: fast, simple, and focused.

Use Fast Lane when the task is small, reversible, and low risk.

The goal is to move from task to pull request quickly without losing basic quality discipline.

---

## Summary

```text
Task
  -> Developer
  -> Tester
  -> Reviewer when risk is meaningful
  -> Product Manager when scope or product behavior changes
  -> Specialist reviewer if needed
  -> Human approval
```

Fast Lane is not careless.  
It is simply lightweight.

---

## When to use Fast Lane

Use Fast Lane for:

```yaml
use_fast_lane_for:
  - small bug fixes
  - small features
  - MVP experiments
  - UI copy changes
  - internal tools
  - isolated backend endpoints
  - simple tests
  - documentation updates
  - low-risk refactors
```

Examples:

```yaml
examples:
  - Add a health check endpoint
  - Fix form validation message
  - Add a unit test for a helper function
  - Update README setup command
  - Add a small API response field
```

---

## When not to use Fast Lane

Do not use Fast Lane for:

```yaml
avoid_fast_lane_for:
  - authentication changes
  - authorization changes
  - billing
  - payment logic
  - security-sensitive work
  - database migrations
  - infrastructure changes
  - Kubernetes changes
  - CI/CD pipeline changes
  - large refactors
  - public API breaking changes
  - changes involving customer data
```

Use Full Lane for those.

---

## Roles in Fast Lane

### Product Manager

Optional.

Use PM if the task is vague, needs acceptance criteria, or changes product behavior.

Use Product Manager when:

- behavior changes visible to users or operators
- compatibility tradeoffs appear
- migration or rollout decisions appear
- acceptance criteria are unclear

### Developer

Required.

Implements the change and prepares a small PR.

### Tester

Required unless the change is documentation-only.

Validates the behavior and reports failures.

### Reviewer

Optional.

Use Reviewer if:
- risk is medium
- code touches important logic
- Tester is unsure
- human requests review
- PR is larger than expected
- public API or protocol behavior changes
- security, auth, or authorization changes
- production configuration changes
- dependency, runtime, container, CI, or build-system changes
- default-branch merge readiness is being evaluated
- behavior-changing refactors are included
- shared modules or broad surfaces change

Use specialist reviewers only when their area is touched:
- Security Reviewer for security-sensitive or data-risk changes
- UX / Design Reviewer for user-facing UI/UX changes
- Documentation Agent for docs, examples, changelogs, or release notes
- Software Architect Agent only when a supposedly small change affects significant boundaries, contracts, data ownership, runtime dependencies, or quality attributes

### Human

Required.

Human approves final PR and merges.

---

## Fast Lane steps

### Step 1 — Clarify the task

Before implementation, the agent should ensure the task has:

```yaml
task_requirements:
  - title
  - short description
  - acceptance criteria
  - risk level
```

If missing, create reasonable assumptions for low-risk tasks.

For medium or unclear risk, ask the human or use PM.

---

### Step 2 — Implement

Developer should:

```yaml
developer_actions:
  - inspect relevant files
  - keep changes small
  - avoid unrelated edits
  - follow existing patterns
  - add or update tests when useful
  - prepare PR description
```

Developer must not:
- merge
- bypass review
- push directly to protected branch
- commit secrets
- hide failing tests

---

### Step 3 — Validate

Tester should:

```yaml
tester_actions:
  - run relevant tests
  - check acceptance criteria
  - identify regression risk
  - report clearly
```

Tester should not run giant suites unless needed.

---

### Step 4 — Optional review

Reviewer should check:

```yaml
reviewer_checks:
  - correctness
  - scope control
  - maintainability
  - obvious security concerns
  - test adequacy
```

Reviewer should avoid nitpicks in Fast Lane.

---

### Step 4b — Product Owner / Product Manager check if needed

Product Manager should check:

```yaml
product_checks:
  - user or operator-visible behavior change
  - compatibility tradeoff
  - migration or rollout decision
  - unclear acceptance criteria
```

Human remains responsible for final product direction and risk acceptance.

---

### Step 4c — Specialist review if needed

Specialist reviewers should check only their area and keep findings actionable.

Use:

```yaml
specialist_reviewers:
  security_reviewer: security, privacy, data, auth, secrets, infrastructure risk
  ux_design_reviewer: usability, accessibility, visual quality, responsive behavior
  documentation_agent: docs accuracy, examples, changelog, release notes
  software_architect_agent: boundaries, dependency direction, contracts, data ownership, quality attributes
```

---

### Step 5 — Human approval

Human reviews and decides:

```yaml
human_decisions:
  - approve
  - request changes
  - close / abandon
  - escalate to Full Lane
```

Only the human merges.

---

## Fast Lane output expectations

A completed Fast Lane task should produce:

```yaml
outputs:
  - focused code change
  - small PR
  - test result or explanation
  - clear PR description
  - specialist review result if required
  - human approval before merge
```

---

## Escalation triggers

Escalate Fast Lane to Full Lane if:

```yaml
escalate_if:
  - task becomes larger than expected
  - security risk appears
  - database migration appears
  - default-branch merge risk appears
  - supply-chain risk appears
  - compatibility rollout decision appears
  - integration behavior spans external systems
  - unclear product decision appears
  - multiple systems are affected
  - tester cannot validate safely
  - reviewer identifies high risk
```

Escalation is not failure.  
It is a quality control mechanism.

---

## Fast Lane done definition

Fast Lane work is done when:

```yaml
done:
  - implementation matches acceptance criteria
  - relevant validation is complete
  - PR is clear and small
  - no critical unresolved findings remain
  - human approves
  - human merges if desired
```

---

## Agent instruction

When acting under Fast Lane:

```text
Move quickly.
Keep scope small.
Make quality visible.
Escalate when risk appears.
Do not merge.
```
