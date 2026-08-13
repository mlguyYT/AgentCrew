# Skill: Software Architecture

## Purpose

Use this Skill to design or review modular software systems with explicit quality attributes, boundaries, tradeoffs, and evolution paths.

It supports Software Architect Agent, Developer, Product Manager, and Reviewer when a task has meaningful architecture impact.

---

## Applies when

Use this Skill for:

- system design or architecture decisions
- service, module, component, or bounded-context boundaries
- public API, protocol, event, schema, or data-ownership changes
- large or cross-cutting refactors
- scalability, availability, resilience, performance, security, or operability requirements
- dependency direction and integration design
- architecture reviews and ADRs

---

## Detection triggers

```yaml
triggers:
  task_text:
    - software architecture
    - system design
    - architecture decision
    - architecture review
    - service boundary
    - module boundary
    - bounded context
    - dependency direction
    - data ownership
    - scalability
    - resilience
    - quality attribute
    - ADR
  files:
    - "docs/architecture/**"
    - "docs/adr/**"
    - "**/architecture/**"
    - "**/*adr*.md"
```

---

## Instructions

Start from evidence:

- clarify the user outcome, constraints, risk, and measurable quality attributes
- inspect the existing architecture before proposing changes
- identify affected boundaries, contracts, data ownership, and dependency direction
- model important runtime flows and failure paths
- compare at least two realistic options for consequential decisions
- state benefits, costs, migration impact, rollback options, and rejected alternatives
- prefer a modular monolith or existing deployment shape until independent scaling, ownership, isolation, or release needs justify distribution
- keep policy and domain rules separate from frameworks, transport, persistence, and vendors where practical
- preserve public contracts unless behavior change is explicitly approved
- define architecture fitness checks such as dependency rules, contract tests, performance budgets, schema compatibility checks, or cycle detection
- record when the decision should be revisited

Use diagrams only when they clarify boundaries or flows. Text plus a small dependency or sequence view is usually enough.

---

## Testing guidance

Architecture validation should be executable where practical:

- dependency and import-boundary checks
- contract and compatibility tests
- integration tests across changed boundaries
- migration and rollback rehearsal
- load or performance tests tied to stated budgets
- resilience tests for critical failure paths
- observability checks for new runtime dependencies

Do not claim scalability, resilience, or maintainability without evidence or a defined verification path.

---

## Review checklist

- decision and scope are explicit
- quality attributes are prioritized and measurable
- boundaries and dependency direction are clear
- data ownership and consistency expectations are clear
- failure modes, security, observability, and operations are addressed
- options and tradeoffs are documented
- migration, compatibility, and rollback are practical
- architecture fitness checks can detect drift
- design fits current needs without speculative complexity
- human-only decisions remain pending until approved

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - architecture_by_framework_preference
  - premature_microservices
  - shared_database_without_clear_ownership
  - circular_dependencies
  - business_logic_in_transport_or_persistence_layers
  - distributed_workflow_without_failure_and_idempotency_design
  - quality_claims_without_measures
  - irreversible_migration_without_rollback
  - abstractions_created_only_for_hypothetical_future_use
  - diagrams_that_do_not_match_runtime_reality
```

---

## Output note

If relevant, include:

```md
## Skills Applied
- software-architecture
```
