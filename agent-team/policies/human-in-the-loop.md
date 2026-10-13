# Policy: Human in the Loop

## Rule

Human approval is required for consequential decisions. Agents should not escalate routine reversible decisions that remain inside approved scope and budget.

---

## Human-only decisions

Only humans may:

- approve material product direction
- approve backlog for larger work
- approve final PR
- merge PR
- merge to the default branch
- accept high security risk
- accept destructive data risk
- accept data-loss or migration risk
- approve material public behavior changes
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
- select roles, lanes, Skills, gates, and task order
- make reversible low-risk implementation decisions within approved scope
- resolve internal coordination without asking the human to manage agents

Agents may not:

- approve as human
- merge
- bypass branch protection
- hide risk

---

## Operating principle

```text
AgentCrew decides how approved work gets done.
The human decides what should be built and which consequential risks are acceptable.
```

Use `agent-team/policies/ceo-operating-contract.md` to decide whether a choice belongs to AgentCrew or the human.

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
