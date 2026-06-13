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

- treat AgentCrew as the primary routing layer for project work
- classify the request
- choose Fast Lane or Full Lane
- choose the starting role
- load relevant Skills
- run the workflow until human approval is needed

Claude Code should not switch to another workflow, skill pack, or agent methodology before AgentCrew has routed the request, unless the user explicitly asks for that other system.

If a local skill also matches the request, Claude Code should keep AgentCrew as the classifier and use that skill only as an execution aid after the AgentCrew route is chosen.

## Notes

Claude Code treats `CLAUDE.md` as context, not hard enforcement. Keep the loader strong enough to establish AgentCrew as the default router, while leaving detailed role, lane, Skill, and gate instructions in the external checkout.
