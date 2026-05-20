# Human Decision Queue

## Purpose

The Human Decision Queue lists decisions that only the human can make.

It gives product builders a short, explicit queue of approvals, rejections, risk acceptances, and tradeoffs instead of burying them inside agent reports.

---

## Project Artifact

Use this project-local file when decisions are pending:

```text
.agent-state/human-decisions.md
```

Use this template from AgentCrew:

```text
agent-team/templates/human-decision-queue.md
```

The queue belongs to the target project, not the external AgentCrew checkout.

---

## When To Create It

Create or update the queue when the task requires human approval for:

- final product direction
- backlog approval for large work
- PR approval or default-branch merge
- security or data-risk acceptance
- data loss or migration risk
- public behavior change
- rollout or compatibility tradeoff
- legacy insecure compatibility
- force-push or shared history rewrite
- quality gate override

---

## Status Dashboard

`agentcrew status` reads the queue when it exists:

```bash
~/AgentCrew/bin/agentcrew status --project .
```

The dashboard shows whether a decision queue is present and the first pending decision.

---

## Agent Rule

Agents may recommend an option. Agents may not mark human-only risk decisions as approved, rejected, or deferred.

Use:

```text
agent-team/playbooks/human-decision-queue.md
agent-team/checklists/human-approval.md
agent-team/policies/human-in-the-loop.md
```
