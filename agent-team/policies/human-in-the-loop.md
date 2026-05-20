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
- merge to the default branch
- accept high security risk
- accept destructive data risk
- accept data-loss or migration risk
- change public behavior
- enable legacy insecure compatibility
- force-push or rewrite shared history
- override quality gates
- resolve pending decision queue items involving risk acceptance

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

---

## Decision queue

When a human-only decision is needed, agents should record it in:

```text
.agent-state/human-decisions.md
```

Use:

```text
agent-team/playbooks/human-decision-queue.md
agent-team/templates/human-decision-queue.md
```

Agents may recommend an option, but only the human may approve, reject, defer, or accept risk.
