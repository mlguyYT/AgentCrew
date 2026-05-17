# GitHub Copilot Adapter

## Purpose

Use this adapter when configuring GitHub Copilot or Copilot Coding Agent to use AgentCrew.

Copilot environments can differ between local editor chat, repository instructions, and hosted coding-agent execution. AgentCrew therefore documents the loader text instead of assuming one automatic global file works everywhere.

## Recommended instruction text

Add this instruction where your Copilot environment supports custom coding-agent instructions:

```text
AgentCrew is installed at ~/AgentCrew.

For coding tasks, apply AgentCrew automatically.
Read ~/AgentCrew/AGENTS.md and the relevant files under ~/AgentCrew/agent-team/.

Users do not need to name AgentCrew, a role, a lane, or a Skill.
Classify the request, choose Fast Lane or Full Lane, choose the starting role, load relevant Skills, keep human approval final, and do not merge pull requests.
```

## Expected behavior

When a user asks:

```text
Fix the login validation bug.
```

Copilot should route the work through AgentCrew without requiring the user to repeat the loading prompt.
