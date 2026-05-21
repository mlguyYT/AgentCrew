# Implementation Readiness

## Purpose

Implementation readiness checks whether AgentCrew has enough task state to begin coding safely.

It is useful after task intake, acceptance criteria, or work planning, and before the Developer starts changing files.

---

## Run

From a target project:

```bash
~/AgentCrew/bin/agentcrew ready
```

From anywhere:

```bash
~/AgentCrew/bin/agentcrew ready --project /path/to/project
```

This creates or updates:

```text
.agent-state/readiness-report.md
```

Use `--dry-run` to preview and `--force` when intentionally replacing an existing readiness report.

---

## What It Checks

- current task presence
- task brief presence
- work plan presence
- pending human decisions
- blocking open questions
- whether the next action is clear enough for the selected owner

---

## Rules

- Missing artifacts do not always block tiny low-risk fixes.
- Full Lane, high-risk, release, incident, migration, compatibility, or broad feature work should have a work plan.
- Vague or user-visible work should have a task brief.
- Human-only decisions block implementation until resolved by the human.

See:

```text
agent-team/playbooks/implementation-readiness.md
agent-team/templates/readiness-report.md
agent-team/checklists/implementation-readiness.md
```
