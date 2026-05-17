# Claude Code Adapter

## Purpose

Use this adapter to make Claude Code load AgentCrew automatically.

After one-time installation, users should be able to open any project and enjoy development with AgentCrew.

## Recommended install

From the AgentCrew checkout:

```bash
~/AgentCrew/bin/agentcrew install --agent claude
```

This updates:

```text
~/.claude/CLAUDE.md
```

The installed loader imports:

```text
~/AgentCrew/AGENTS.md
```

Claude Code should then read AgentCrew at session start and apply the workflow automatically.

## Expected behavior

When a user asks:

```text
Fix the login validation bug.
```

Claude Code should:

- classify the request
- choose Fast Lane or Full Lane
- choose the starting role
- load relevant Skills
- run the workflow until human approval is needed

## Notes

Claude Code treats `CLAUDE.md` as context, not hard enforcement. Keep the loader short and let AgentCrew's detailed files remain in the external checkout.
