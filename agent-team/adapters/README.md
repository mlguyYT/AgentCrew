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

After registration, users should be able to open any project and enjoy development with AgentCrew.

## Supported adapters

```text
claude-code.md
codex.md
openclaw.md
hermes.md
cursor.md
copilot.md
```

The installer currently writes global loaders for Claude Code, Codex, OpenClaw, and Hermes Agent.
The default `install` command registers OpenClaw and Hermes Agent when they are detected; `--agent openclaw` or `--agent hermes` forces registration explicitly.
Cursor and GitHub Copilot adapters provide loader text for their custom-instruction surfaces.

For any other host agent, generate the canonical vendor-neutral loader text:

```bash
~/AgentCrew/bin/agentcrew loader
```

Place that output in the host's global or user-level instruction surface. If the host has no persistent instruction mechanism, use the adapter text at session start.

## Rule

If instructions conflict, the root `AGENTS.md` and `agent-team/` folder win.
