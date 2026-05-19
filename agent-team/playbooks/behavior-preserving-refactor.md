# Behavior-Preserving Refactor

## Purpose

This playbook defines how agents should handle refactors where the goal is to improve structure without silently changing behavior.

Refactoring should make the project easier to maintain while preserving contracts unless the task explicitly includes a behavior change.

---

## Behavior Categories

Before and after a refactor, classify observed behavior as:

```yaml
behavior_categories:
  preserved_legacy_behavior: existing behavior intentionally kept
  intentional_behavior_change: behavior changed because the task requires it
  discovered_legacy_bug: questionable behavior found but left for later
```

Do not silently relabel preserved behavior as corrected behavior.
If behavior is questionable but out of scope, document it as a follow-up risk.

---

## Refactor Rules

Agents should:

```yaml
refactor_rules:
  - extract one boundary at a time
  - add tests around existing behavior before changing structure
  - preserve data keys, schemas, event names, API contracts, and external behavior
  - avoid mixing broad refactors with product behavior changes
  - keep commits or PRs small enough to review
  - document any intentional behavior change separately from structural cleanup
```

Examples of external behavior to preserve:

- public API routes and response shapes
- protocol messages and event names
- database schemas and data keys
- configuration names and defaults
- CLI flags and output relied on by users
- client/server compatibility behavior

---

## Testing Expectations

Before refactoring:

- add characterization tests when behavior lacks coverage
- capture current externally visible behavior
- identify contracts that must not change

After refactoring:

- rerun focused tests
- rerun integration tests when behavior spans modules or external systems
- document preserved legacy issues and test gaps

Use:

```text
agent-team/checklists/integration-test-escalation.md
```

when modularization creates or exposes cross-component behavior.
