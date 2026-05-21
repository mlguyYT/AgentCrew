# Implementation Readiness Playbook

## Purpose

Check whether a routed task is ready for implementation before Developer starts changing code.

Implementation readiness helps product builders avoid vague agent work, oversized PRs, missing acceptance criteria, and hidden human-only decisions.

---

## When To Use

Use this playbook when:

```yaml
use_when:
  - before implementation starts
  - after task intake, task brief, or work plan changes
  - before handing work from Product Manager to Developer
  - before resuming a paused task
  - when the human asks whether work is ready to build
```

For tiny low-risk fixes, the check can be brief.

---

## Readiness Inputs

Prefer these project-local artifacts when present:

```text
.agent-state/current-task.md
.agent-state/task-brief.md
.agent-state/work-plan.md
.agent-state/human-decisions.md
```

Do not read or write readiness state inside `agent-team/`.

---

## Required Signals

A task is implementation-ready when:

```yaml
ready_when:
  - current task exists or the request is otherwise clearly routed
  - owner and next action are clear
  - acceptance criteria are clear enough for Tester validation
  - work plan exists for Full Lane, high-risk, broad, or multi-phase work
  - human-only decisions that block implementation are resolved
  - no known blocker is hidden in open questions
```

---

## Not Ready Signals

```yaml
not_ready_when:
  - missing current task for non-trivial work
  - missing task brief for vague, medium-risk, high-risk, or user-visible behavior change
  - missing work plan for Full Lane, high-risk, incident, release, migration, or broad feature work
  - pending human decision blocks implementation
  - open question blocks scope, risk, access, or validation
  - next action is not actionable
```

---

## Command

Use:

```bash
~/AgentCrew/bin/agentcrew ready --project .
```

Use `--dry-run` to preview and `--force` only when replacing `.agent-state/readiness-report.md`.

---

## Artifact

Write project-specific readiness reports to:

```text
.agent-state/readiness-report.md
```

Use:

```text
agent-team/templates/readiness-report.md
```
