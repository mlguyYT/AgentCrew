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
- [ ] no secrets are present
- [ ] you are comfortable merging

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
