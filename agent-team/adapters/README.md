# Tool Adapters

This folder explains how to connect the Agent Team workflow to different AI coding tools.

The canonical source is always:

```text
AGENTS.md
agent-team/
```

Adapter files should not duplicate the full workflow.

They should only point the tool to the canonical files.

## Supported adapter examples

```text
.codex/AGENTS.md
.github/copilot-instructions.md
.cursor/rules/agent-team.md
.claude/CLAUDE.md
```

## Rule

If instructions conflict, the root `AGENTS.md` and `agent-team/` folder win.
