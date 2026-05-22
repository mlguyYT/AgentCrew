# Hermes Agent Adapter

## Purpose

Use this adapter to make Hermes Agent apply AgentCrew automatically for coding work.

AgentCrew remains an external Markdown workflow. Hermes Agent remains the runtime, profile, memory, session, gateway, tool-policy, and credential layer.

## Recommended Install

From the AgentCrew checkout:

```bash
~/AgentCrew/bin/agentcrew install --agent hermes
```

This updates the active Hermes profile persona file:

```text
~/.hermes/SOUL.md
```

Hermes loads `SOUL.md` from `HERMES_HOME`, so the installer writes only a small AgentCrew-managed loader block and leaves existing persona text outside that block intact.

For a custom Hermes home:

```bash
HERMES_HOME=/path/to/hermes-home ~/AgentCrew/bin/agentcrew install --agent hermes
```

For a named Hermes profile:

```bash
HERMES_PROFILE=work ~/AgentCrew/bin/agentcrew install --agent hermes
```

Named profiles resolve to:

```text
~/.hermes/profiles/<profile>/SOUL.md
```

If `~/.hermes/active_profile` names an existing non-default profile and no explicit `HERMES_HOME` or `HERMES_PROFILE` is set, the installer uses that active profile.

The installed loader points Hermes Agent to:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
```

## Expected Behavior

When a user asks:

```text
Fix the login validation bug.
```

Hermes Agent should:

- keep its own identity, memory, skills, session history, gateway, profile, tool policy, and credential handling
- apply AgentCrew for coding-team workflow
- classify the request
- choose Fast Lane or Full Lane
- choose the starting role
- load relevant Skills
- run the workflow until human approval is needed

## Boundaries

AgentCrew does not replace Hermes Agent runtime behavior.

AgentCrew must not override:

- Hermes Agent identity instructions
- Hermes Agent memory policy
- Hermes Agent skills system
- Hermes Agent session history
- Hermes Agent gateway or channel behavior
- Hermes Agent profile isolation
- Hermes Agent tool approval policy
- Hermes Agent credential handling

If instructions conflict, preserve safety, privacy, and human approval.
