# Policy: Scope Control

## Rule

Agents must keep work within the task scope.

---

## Why

Scope creep causes:

- large PRs
- slow reviews
- more bugs
- unclear ownership
- harder rework

---

## Allowed

Agents may:

- make changes required by the task
- update tests for changed behavior
- update docs directly related to the change
- make small supporting changes if clearly necessary

---

## Not allowed without explicit instruction

Agents should not:

- refactor unrelated code
- rename unrelated files
- change architecture broadly
- update dependencies unnecessarily
- change formatting across many files
- modify unrelated tests

---

## If more work is discovered

Create a follow-up task instead of expanding the PR.

Use:

```text
agent-team/templates/task.md
```

---

## Operating principle

```text
One task.
One focused PR.
Follow-up work gets its own task.
```
