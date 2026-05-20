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
- current task fields when `.agent-state/current-task.md` exists
- latest test, review, security, UX, and documentation report presence
- decisions, handoff, memory, and latest saved session
- open questions and the human-approval reminder

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

## Owner

## Status

## Next Action

## Open Questions
```

Missing files or sections are reported as `not set`. That is normal for projects that have not saved AgentCrew state yet.

---

## How Agents Should Use It

Use `agentcrew status` before resuming work or handing off between roles. It gives a compact view of:

- what project is active
- whether the worktree has changes
- what AgentCrew state exists
- what the next visible action is
- whether human attention is needed

Do not treat status as a substitute for inspecting task-specific files before editing code.
