# Pull Request Process

## Purpose

This playbook defines the standard PR process for the Agent Team workflow.

The PR process ensures that code changes are:

- small
- traceable
- tested
- reviewed
- human-approved

---

## Golden rule

```text
Agents may create or update PRs.
Agents may not merge PRs.
```

---

## Standard PR flow

```text
Developer
  -> Pull Request
  -> Tester
  -> Reviewer
  -> Human approval
  -> Human merge
```

For low-risk Fast Lane work:

```text
Developer
  -> Pull Request
  -> Tester
  -> Human approval
```

Reviewer is optional for low-risk work.

---

## PR ownership

Each PR must have one primary Developer Agent owner.

```yaml
pr_ownership:
  primary_developer_required: true
  multiple_primary_developers_allowed: false
  rework_returns_to_original_developer: true
```

Supporting agents may comment or validate, but should not create competing changes on the same branch unless explicitly instructed.

---

## Branch rules

Agents must not work directly on protected branches.

Protected branches usually include:

```yaml
protected_branches:
  - main
  - master
  - develop
  - release/*
```

Recommended branch format:

```text
agent/<role>/<task-id>
```

Examples:

```text
agent/developer/task-001
agent/developer-backend/task-042
agent/docs/update-readme
```

---

## PR title format

Recommended:

```text
[Agent][TASK-ID] Short description
```

Example:

```text
[Agent][TASK-001] Add project creation endpoint
```

---

## PR description requirements

Every PR should include:

```md
## Summary
What changed.

## Task
Task ID or description.

## Acceptance Criteria
- [x] criterion 1
- [x] criterion 2

## Tests
Commands run and results.

## Risk
Low / Medium / High

## Notes for Reviewer
Anything important to inspect.
```

Use:

```text
agent-team/templates/pr-description.md
```

---

## Developer responsibilities

Developer must:

```yaml
developer_responsibilities:
  - implement task
  - keep changes focused
  - update tests when needed
  - prepare PR description
  - document tests run
  - mention limitations
```

Developer must not:

```yaml
developer_forbidden:
  - merge PR
  - bypass review
  - hide failing tests
  - commit secrets
  - make unrelated changes
```

---

## Tester responsibilities

Tester must:

```yaml
tester_responsibilities:
  - validate acceptance criteria
  - run relevant tests
  - document results
  - request rework if behavior fails
```

Tester may not merge.

---

## Reviewer responsibilities

Reviewer must:

```yaml
reviewer_responsibilities:
  - check correctness
  - check scope
  - check maintainability
  - check architecture fit
  - check security concerns
  - check test adequacy
```

Reviewer may mark ready for human review.

Reviewer may not merge.

---

## Human responsibilities

Human decides:

```yaml
human_responsibilities:
  - approve final PR
  - request changes
  - merge
  - reject or close PR
```

---

## PR labels

Recommended labels:

```yaml
labels:
  - agent-generated
  - needs-test
  - needs-review
```

Optional labels:

```yaml
risk_labels:
  - risk-low
  - risk-medium
  - risk-high

role_labels:
  - backend
  - frontend
  - infra
  - docs
  - test
```

---

## When to split a PR

Split PR if:

```yaml
split_if:
  - too many unrelated files changed
  - multiple features included
  - refactor mixed with behavior change
  - reviewer cannot understand scope quickly
  - risky change can be isolated
```

---

## PR done definition

A PR is ready for human approval when:

```yaml
ready_for_human:
  - acceptance criteria addressed
  - relevant tests run or limitation documented
  - tester passed or provided acceptable report
  - reviewer passed if required
  - no critical unresolved comments
  - PR description is clear
```

---

## Agent instruction

When working with PRs:

```text
Make changes visible.
Keep scope small.
Document tests honestly.
Route failures to rework.
Never merge.
```
