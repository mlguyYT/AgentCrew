# Tool Adapters

This folder explains how to connect the AgentCrew workflow to different AI coding tools.

The canonical source is always:

```text
AGENTS.md
agent-team/
```

Adapter files should not duplicate the full workflow.

They should only point the tool to the canonical files.

## Preferred model

Install AgentCrew once outside target projects:

```text
~/AgentCrew/
```

Then register a tiny global loader:

```bash
~/AgentCrew/bin/agentcrew install
```

After registration, users should be able to open any project and ask for the outcome without saying `Load AgentCrew`.

## Supported adapters

```text
claude-code.md
codex.md
cursor.md
copilot.md
```

The installer currently writes global loaders for Claude Code and Codex.
Cursor and GitHub Copilot adapters provide loader text for their custom-instruction surfaces.

## Rule

If instructions conflict, the root `AGENTS.md` and `agent-team/` folder win.
