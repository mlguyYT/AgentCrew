# Policy: Human in the Loop

## Rule

Human approval is required for important decisions.

---

## Human-only decisions

Only humans may:

- approve product direction
- approve backlog for larger work
- approve final PR
- merge PR
- accept high security risk
- accept destructive data risk
- override quality gates

---

## Agent permissions

Agents may:

- recommend
- plan
- implement
- test
- review
- request rework

Agents may not:

- approve as human
- merge
- bypass branch protection
- hide risk

---

## Operating principle

```text
Agents accelerate work.
Humans own judgment.
```
