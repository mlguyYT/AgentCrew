# Acceptance Criteria

## Purpose

AgentCrew can turn a plain request into a compact task brief with provisional acceptance criteria, scope, test plan, gates, and open questions.

This helps product builders start quickly without having to write a full ticket first.

---

## Create A Task Brief

From a target project:

```bash
~/AgentCrew/bin/agentcrew brief --task "Fix the login form so empty email shows a validation message"
```

This creates:

```text
.agent-state/task-brief.md
```

Use `--dry-run` to preview and `--force` only when intentionally replacing the current brief.

---

## What It Contains

- request
- selected recipe
- lane, risk, quality profile, and owner
- desired outcome
- user/operator impact
- provisional acceptance criteria
- scope and out-of-scope items
- test plan
- review and human approval gates
- open questions

---

## Rules

- Criteria should be observable and testable.
- Keep one task small enough for a focused PR.
- Preserve behavior unless behavior change is explicit.
- Record human-only decisions separately in `.agent-state/human-decisions.md`.
- Do not store secrets, raw customer data, local paths, private key paths, or long logs.

See:

```text
agent-team/playbooks/acceptance-criteria.md
agent-team/templates/task-brief.md
agent-team/checklists/acceptance-criteria.md
```
