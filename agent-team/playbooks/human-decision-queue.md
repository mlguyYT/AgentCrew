# Human Decision Queue Playbook

## Purpose

Collect decisions that only a human may make, so product builders can approve, reject, defer, or request changes without reading every agent detail.

Agents may recommend an option. Agents must not decide on behalf of the human.

---

## When To Use

Create or update the human decision queue when work involves:

```yaml
human_decision_required_for:
  - final product direction
  - backlog approval for large work
  - pull request approval
  - merge to default branch
  - security or data-risk acceptance
  - data loss or migration risk
  - public behavior change
  - compatibility or rollout tradeoff
  - enabling legacy insecure compatibility
  - force-push or shared history rewrite
  - overriding a quality gate
  - unclear acceptance criteria that materially changes outcome
```

Also update it when a Reviewer, Security Reviewer, Product Manager, Tester, or Human identifies a decision that cannot be resolved by implementation alone.

---

## Artifact Location

Use this project-local file:

```text
.agent-state/human-decisions.md
```

Do not store project decisions in `agent-team/`.

Use the template:

```text
agent-team/templates/human-decision-queue.md
```

---

## Decision Entry Requirements

Each decision should include:

```yaml
required_fields:
  - id
  - status
  - decision_needed
  - context
  - options
  - agent_recommendation
  - evidence
  - risk_if_approved
  - risk_if_deferred
  - requested_by
  - needed_before
```

Keep each entry short. Link or reference reports instead of copying long evidence.

---

## Status Values

```yaml
status_values:
  pending: waiting for human decision
  approved: human approved
  rejected: human rejected
  changes_requested: human requested changes
  deferred: moved to later work
  superseded: replaced by a newer decision
```

Only the human can move a decision to `approved`, `rejected`, or `deferred` when risk acceptance is involved.

---

## Agent Output Rule

When a human decision is required, agents should say:

```text
Human decision needed: <short decision>.
Recommendation: <recommended option>.
Reason: <one sentence>.
Blocking: yes/no.
```

Do not bury human decisions inside long reports.

---

## Blocking Rule

A pending human decision blocks progress when it affects:

```yaml
blocking_if_pending:
  - security risk acceptance
  - data loss or migration acceptance
  - public behavior change
  - legacy insecure compatibility
  - default-branch merge
  - force-push or history rewrite
  - quality gate override
```

Agents may continue safe preparatory work only if it does not pre-decide the pending human choice.

---

## Status Dashboard

`agentcrew status` reads `.agent-state/human-decisions.md` when present and surfaces the queue under Human Attention.

If the file is missing, status reports the decision queue as `not set`.
