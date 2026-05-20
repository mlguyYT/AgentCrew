# Human Approval Checklist

## Purpose

This checklist helps the human make final decisions.

Agents can recommend, but human approval is required.

---

## Before approving concept

- [ ] problem is clear
- [ ] target user is clear
- [ ] expected value is clear
- [ ] MVP scope is reasonable
- [ ] major risks are visible

---

## Before approving backlog

- [ ] tasks are small
- [ ] acceptance criteria are clear
- [ ] risky work uses Full Lane
- [ ] dependencies are visible
- [ ] out-of-scope items are clear

---

## Before approving PR

- [ ] PR is focused
- [ ] acceptance criteria are addressed
- [ ] tests are documented
- [ ] reviewer concerns are resolved or accepted
- [ ] risk is acceptable
- [ ] security, data-loss, migration, compatibility, and public-behavior tradeoffs are explicit
- [ ] default-branch merge readiness is documented when applicable
- [ ] no secrets are present
- [ ] you are comfortable merging

---

## Human-Only Decisions

Only the human may approve:

- merging to the default branch
- accepting security risk
- accepting data-loss or migration risk
- changing public behavior
- enabling legacy insecure compatibility
- force-pushing or rewriting shared history
- overriding quality gates

---

## Decision Queue

- [ ] pending human-only decisions are listed in `.agent-state/human-decisions.md` when needed
- [ ] each decision has options and agent recommendation separated
- [ ] risk acceptance is explicit
- [ ] no agent has marked a human-only decision approved

---

## Human decision options

```yaml
decisions:
  - approve
  - request_changes
  - split_task
  - send_back_to_pm
  - abandon
  - pause
```
