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

Check registration:

```bash
~/AgentCrew/bin/agentcrew status
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
- `~/AgentCrew/bin/agentcrew status` shows the expected registration
- a new agent session can respond to a normal task without a `Load AgentCrew` prompt

If a tool does not appear to load AgentCrew, ask it which instruction files were loaded at session start, then use the relevant adapter file.
