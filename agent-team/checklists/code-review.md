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
- [ ] Is preserved legacy behavior distinguished from intentional behavior change?
- [ ] Are discovered legacy bugs documented as follow-up instead of silently corrected?
- [ ] Is the PR small enough to review?

---

## Maintainability

- [ ] Is the code understandable?
- [ ] Are names clear?
- [ ] Is complexity justified?
- [ ] Does it follow project conventions?
- [ ] Is the implementation modular and loosely coupled?
- [ ] Does it preserve clean architecture boundaries?
- [ ] Is business logic in the correct layer for this project?
- [ ] Will this scale without forcing a broad rewrite soon?
- [ ] Would a future developer understand this?

---

## Tests

- [ ] Are relevant tests present?
- [ ] Do tests cover changed behavior?
- [ ] Is overall coverage at least 70 percent when coverage tooling exists?
- [ ] If coverage is below 70 percent, is the gap documented for human decision?
- [ ] Are test results documented?
- [ ] Are important negative cases covered?
- [ ] Are flaky or skipped tests explained?
- [ ] Were integration tests considered when behavior spans modules or external systems?

---

## Security

- [ ] No secrets committed
- [ ] Inputs are validated
- [ ] Permissions are not broadened unnecessarily
- [ ] Sensitive data is not logged
- [ ] Auth behavior is not weakened
- [ ] Dependency, lockfile, runtime, container, CI, or build-system changes passed the supply-chain gate

---

## Operations

- [ ] Config changes are documented
- [ ] Migrations are safe if present
- [ ] Rollback risk is understood
- [ ] CI/CD impact is clear
- [ ] Compatibility rollout is documented for API, protocol, auth, config, or client/server changes
- [ ] Default-branch merge readiness is documented if preparing merge

---

## Output Discipline

Separate review output into:

- blocking issues
- non-blocking risks
- preserved legacy issues
- test gaps
- product or rollout decisions
- next implementation phase

---

## Recommendation

Reviewer should choose one:

```yaml
recommendation:
  - ready_for_human_review
  - rework_required
  - needs_human_decision
```
