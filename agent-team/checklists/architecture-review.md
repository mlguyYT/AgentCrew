# Architecture Review Checklist

## Purpose

Use this checklist when architecture decision or architecture review routing is triggered.

## Decision

- [ ] problem and decision scope are explicit
- [ ] current architecture and constraints were inspected
- [ ] assumptions and unknowns are visible
- [ ] realistic alternatives, including no change, were considered
- [ ] recommendation and consequences are documented

## Design

- [ ] prioritized quality attributes and their measurable scenarios are explicit
- [ ] module, service, and integration boundaries are clear
- [ ] dependency direction is intentional and enforceable
- [ ] domain rules are not coupled unnecessarily to frameworks or vendors
- [ ] data ownership, consistency, and schema/API contracts are explicit
- [ ] security, privacy, failure modes, and observability are addressed
- [ ] design is proportionate to current needs and avoids speculative complexity

## Evolution

- [ ] compatibility and migration path are documented
- [ ] rollback or recovery path is practical
- [ ] significant irreversible choices require human approval
- [ ] revisit conditions are recorded

## Fitness

- [ ] architecture constraints have automated checks where practical
- [ ] integration-test need was evaluated
- [ ] performance or resilience claims have measurable validation
- [ ] Reviewer can compare implementation against the decision
