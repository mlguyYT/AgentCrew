# Automatic AgentCrew Loading

## Purpose

AgentCrew is meant to be installed once outside project repositories, then recognized by coding agents automatically.

The intended user experience is:

```text
Open any project.
Ask for the outcome.
AgentCrew handles routing, lane selection, roles, Skills, testing, review, memory, and human approval gates.
```

Users should not need to say `Load AgentCrew` after one-time registration.

---

## One-time setup

Clone AgentCrew once:

```bash
git clone https://github.com/mlguyYT/AgentCrew.git ~/AgentCrew
```

Register AgentCrew with supported agents:

```bash
~/AgentCrew/bin/agentcrew install
```

This registers Claude Code and Codex, and registers OpenClaw when OpenClaw is detected on the machine.

Check setup health and status:

```bash
~/AgentCrew/bin/agentcrew doctor
~/AgentCrew/bin/agentcrew status --project .
```

After that, from any project, ask normally:

```text
Fix the login form so empty email shows a validation message.
```

---

## What the installer does

The installer writes a small global loader instead of copying AgentCrew into each project.

Supported automatic registrations:

```text
Claude Code -> ~/.claude/CLAUDE.md
Codex       -> ${CODEX_HOME:-~/.codex}/AGENTS.md
OpenClaw    -> ${OPENCLAW_STATE_DIR:-~/.openclaw}/workspace/AGENTS.md
```

The loader points the agent to:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
```

It tells the agent to:

- apply AgentCrew automatically
- classify the request
- choose Fast Lane or Full Lane
- choose the starting role
- load relevant Skills
- keep handoffs compact
- keep human approval final
- avoid autonomous merge

---

## Tool support

### Claude Code

Use:

```bash
~/AgentCrew/bin/agentcrew install --agent claude
```

This updates:

```text
~/.claude/CLAUDE.md
```

### Codex

Use:

```bash
~/AgentCrew/bin/agentcrew install --agent codex
```

This updates:

```text
${CODEX_HOME:-~/.codex}/AGENTS.md
```

Some Codex clients may vary in how they load global `AGENTS.md`. If automatic loading is not visible in a session, add a project-local adapter or explicitly ask Codex to read `~/AgentCrew/AGENTS.md`.

### OpenClaw

Use:

```bash
~/AgentCrew/bin/agentcrew install --agent openclaw
```

This updates:

```text
~/.openclaw/workspace/AGENTS.md
```

For custom OpenClaw state:

```bash
OPENCLAW_STATE_DIR=/path/to/openclaw-state ~/AgentCrew/bin/agentcrew install --agent openclaw
```

For named OpenClaw profiles:

```bash
OPENCLAW_PROFILE=work ~/AgentCrew/bin/agentcrew install --agent openclaw
```

OpenClaw should keep its own identity, memory, channel, heartbeat, gateway, and safety behavior. AgentCrew only supplies the coding-team workflow.

The default `agentcrew install` command also registers OpenClaw when OpenClaw is detected. Use `--agent openclaw` when you want to create the loader explicitly.

### Cursor and GitHub Copilot

Use the adapter text under:

```text
agent-team/adapters/cursor.md
agent-team/adapters/copilot.md
```

These tools can have version-specific or UI-managed instruction locations, so AgentCrew documents the loader text instead of assuming one global file works everywhere.

---

## Project-local adapters

Project-local adapters are optional. Use them only when a tool does not honor global instructions.

If needed, create the smallest possible adapter in the target project and point it to the external AgentCrew checkout:

```text
Read ~/AgentCrew/AGENTS.md and ~/AgentCrew/agent-team/.
Apply AgentCrew automatically.
```

Do not copy the full AgentCrew package into every project.

---

## Verification

A successful setup means:

- `~/AgentCrew/AGENTS.md` exists
- `~/AgentCrew/agent-team/` exists
- `~/AgentCrew/bin/agentcrew doctor` reports zero failures
- `~/AgentCrew/bin/agentcrew status` shows expected registrations and a project dashboard
- a new agent session can respond to a normal task without a `Load AgentCrew` prompt

If a tool does not appear to load AgentCrew, ask it which instruction files were loaded at session start, then use the relevant adapter file.

To inspect the project stack and preview routing, run:

```bash
~/AgentCrew/bin/agentcrew detect-project --project .
~/AgentCrew/bin/agentcrew classify --project . --task "Fix the login validation bug"
```
