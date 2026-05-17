# Cursor Adapter

## Purpose

Use this adapter when configuring Cursor to use AgentCrew.

Cursor rule storage can vary by version and workspace setup, so AgentCrew does not assume a universal filesystem location for automatic installation.

## Recommended rule text

Add this as a global or user rule in Cursor:

```text
AgentCrew is installed at ~/AgentCrew.

For all coding tasks, apply AgentCrew automatically.
Read ~/AgentCrew/AGENTS.md and the relevant files under ~/AgentCrew/agent-team/.

Users do not need to name AgentCrew, a role, a lane, or a Skill.
Classify the request, choose Fast Lane or Full Lane, choose the starting role, load relevant Skills, keep human approval final, and do not merge pull requests.
```

## Expected behavior

When a user asks:

```text
Fix the login validation bug.
```

Cursor should route the work through AgentCrew without requiring the user to repeat the loading prompt.
