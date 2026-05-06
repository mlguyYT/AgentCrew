# Code Review Checklist

## Purpose

This checklist helps Reviewer Agents and humans review PRs consistently.

---

## Correctness

- [ ] Does the code solve the task?
- [ ] Are acceptance criteria satisfied?
- [ ] Are edge cases handled?
- [ ] Are error states handled?
- [ ] Does behavior match existing patterns?

---

## Scope

- [ ] Is the PR focused?
- [ ] Are unrelated changes avoided?
- [ ] Are refactors separated from feature changes?
- [ ] Is the PR small enough to review?

---

## Maintainability

- [ ] Is the code understandable?
- [ ] Are names clear?
- [ ] Is complexity justified?
- [ ] Does it follow project conventions?
- [ ] Would a future developer understand this?

---

## Tests

- [ ] Are relevant tests present?
- [ ] Do tests cover changed behavior?
- [ ] Are test results documented?
- [ ] Are important negative cases covered?
- [ ] Are flaky or skipped tests explained?

---

## Security

- [ ] No secrets committed
- [ ] Inputs are validated
- [ ] Permissions are not broadened unnecessarily
- [ ] Sensitive data is not logged
- [ ] Auth behavior is not weakened

---

## Operations

- [ ] Config changes are documented
- [ ] Migrations are safe if present
- [ ] Rollback risk is understood
- [ ] CI/CD impact is clear

---

## Recommendation

Reviewer should choose one:

```yaml
recommendation:
  - ready_for_human_review
  - rework_required
  - needs_human_decision
```
