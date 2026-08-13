# Architecture Decisions

## Purpose

Use this playbook for consequential design choices that affect system boundaries, public contracts, data ownership, deployment, quality attributes, or long-term change cost.

The goal is a small, reviewable decision record, not a large architecture document.

---

## Trigger

Use when:

```yaml
architecture_decision_required:
  - new service, subsystem, platform, or major module
  - public API, protocol, event, or schema boundary changes
  - data ownership or consistency model changes
  - cross-cutting or large refactor
  - new runtime dependency or integration boundary
  - scalability, resilience, availability, performance, or operability drives design
  - choice is difficult or expensive to reverse
```

Do not require this playbook for small changes that preserve existing boundaries.

---

## Process

1. State the decision and current context.
2. List constraints and prioritized quality attributes.
3. Describe affected boundaries, contracts, data, and runtime flows.
4. Compare realistic options, including keeping the current design.
5. Select a recommendation with explicit tradeoffs.
6. Define migration, compatibility, rollback, security, and operational impact.
7. Define automated fitness checks and evidence needed after implementation.
8. Identify human-only decisions and the next review point.

Use `agent-team/templates/architecture-report.md`.

---

## Quality Attribute Rule

Avoid vague goals such as "scalable" or "maintainable." Attach a scenario or measurable constraint:

```text
When event volume reaches the agreed threshold, processing latency stays within the stated budget.
When one external dependency fails, the core user action degrades predictably and emits an actionable signal.
When a module changes, dependency checks prevent domain code from importing infrastructure code.
```

Use only attributes relevant to the task.

---

## Decision Ownership

- Software Architect Agent recommends architecture.
- Product Manager owns product scope and behavior clarification.
- Developer implements approved decisions.
- Tester verifies fitness checks and integration behavior.
- Reviewer checks implementation alignment and residual risk.
- Human approves product direction, public behavior, migration/data risk, and irreversible tradeoffs.

---

## Done

Architecture planning is ready for human review when:

- decision scope and assumptions are explicit
- options and consequences are credible
- boundaries and contracts are understandable
- migration and rollback are proportionate to risk
- validation and fitness checks are defined
- unresolved human decisions are visible
