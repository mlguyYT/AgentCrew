# Memory Saving

## Purpose

AgentCrew includes a memory-saving playbook for preserving useful context between sessions.

Use it when work pauses, a meaningful decision is made, or another agent needs handoff context.

## Core files

```text
agent-team/playbooks/memory-saving.md
agent-team/checklists/memory-saving.md
agent-team/templates/memory-summary.md
```

## Recommended use

Ask the agent:

```text
Save memory for the current work using agent-team/playbooks/memory-saving.md.
Do not include secrets or raw logs.
```

If AgentCrew is installed at `~/AgentCrew`, save a local session checkpoint from the target project with:

```bash
~/AgentCrew/agent-team/tools/save-session.sh --project . --title "short title"
```

The checkpoint is written to:

```text
PROJECT_ROOT/.agent-state/sessions/
```

AgentCrew resolves the target git repository root automatically.
If two projects use the same external `~/AgentCrew` checkout, their session checkpoints still stay separate because each project writes to its own `.agent-state/`.

## Storage

Use the human's preferred memory system.

For committed project memory, prefer a project-owned folder such as:

```text
docs/agent-memory/
```

Do not store project memory inside `agent-team/`; that folder is the reusable workflow package.

For active handoff state, use `.agent-state/` and follow:

```text
agent-team/protocols/state-artifacts.md
```

## Safety

Never save secrets, tokens, passwords, private keys, raw customer data, sensitive production data, or large logs.
