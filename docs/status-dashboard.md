# Status Dashboard

## Purpose

`agentcrew status` shows whether AgentCrew is registered with supported coding agents and summarizes the current project state.

It is read-only. It does not create or modify `.agent-state/` files.

---

## Run

From a project directory:

```bash
~/AgentCrew/bin/agentcrew status
```

From anywhere:

```bash
~/AgentCrew/bin/agentcrew status --project /path/to/project
```

The standalone project dashboard is also available inside AgentCrew:

```bash
~/AgentCrew/agent-team/tools/project-status.sh --project /path/to/project
```

---

## What It Shows

`agentcrew status` includes:

- global loader registrations for Claude Code, Codex, and OpenClaw
- project name, git branch, default branch, HEAD, and worktree state
- whether `.agent-state/` exists
- current task fields, including quality profile and recipe, when `.agent-state/current-task.md` exists
- latest test, review, security, UX, and documentation report presence
- project preset, task brief, work plan, readiness report, PR packet, decisions, handoff, memory, and latest saved session
- pending human decision queue, open questions, and the human-approval reminder

---

## Current Task Format

When available, status reads the standard current task sections from:

```text
.agent-state/current-task.md
```

Expected sections:

```md
# Current Task

## Title

## Lane

## Risk

## Quality Profile

## Recipe

## Owner

## Status

## Next Action

## Open Questions
```

Missing files or sections are reported as `not set`. That is normal for projects that have not saved AgentCrew state yet.

Use `agentcrew start --task "..."` to create the current-task artifact from a plain request.

---

## Human Decision Queue

The dashboard also reads:

```text
.agent-state/human-decisions.md
```

When present, it shows whether the decision queue exists and the first pending decision under Human Attention.

Use:

```text
agent-team/templates/human-decision-queue.md
agent-team/playbooks/human-decision-queue.md
```

---

## How Agents Should Use It

Use `agentcrew status` before resuming work or handing off between roles. It gives a compact view of:

- what project is active
- whether the worktree has changes
- what AgentCrew state exists
- what the next visible action is
- whether human attention is needed

Do not treat status as a substitute for inspecting task-specific files before editing code.
