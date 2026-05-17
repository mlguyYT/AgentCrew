# Codex Adapter

## Purpose

Use this adapter to make Codex load AgentCrew automatically when global instructions are honored by the Codex environment.

After one-time installation, users should be able to open any project and enjoy development with AgentCrew.

## Recommended install

From the AgentCrew checkout:

```bash
~/AgentCrew/bin/agentcrew install --agent codex
```

This updates:

```text
${CODEX_HOME:-~/.codex}/AGENTS.md
```

The installed loader points Codex to:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
```

## Expected behavior

When a user asks:

```text
Fix the login validation bug.
```

Codex should:

- classify the request
- choose Fast Lane or Full Lane
- choose the starting role
- load relevant Skills
- run the workflow until human approval is needed

## Notes

Codex behavior can vary by client and version. If a Codex client does not load global `AGENTS.md`, use a project-local adapter or explicitly ask Codex to read `~/AgentCrew/AGENTS.md`.
