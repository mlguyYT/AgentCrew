# OpenClaw Adapter

## Purpose

Use this adapter to make OpenClaw apply AgentCrew automatically for coding work.

AgentCrew remains an external Markdown workflow. OpenClaw remains the runtime, gateway, workspace, channel, memory, and device layer.

## Recommended install

From the AgentCrew checkout:

```bash
~/AgentCrew/bin/agentcrew install --agent openclaw
```

This updates:

```text
~/.openclaw/workspace/AGENTS.md
```

If OpenClaw is using a custom state directory, set:

```bash
OPENCLAW_STATE_DIR=/path/to/openclaw-state ~/AgentCrew/bin/agentcrew install --agent openclaw
```

If OpenClaw is using a named profile, set:

```bash
OPENCLAW_PROFILE=work ~/AgentCrew/bin/agentcrew install --agent openclaw
```

The installed loader points OpenClaw to:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
```

## Expected behavior

When a user asks:

```text
Fix the login validation bug.
```

OpenClaw should:

- keep its own identity, channel, memory, heartbeat, and safety instructions
- apply AgentCrew for coding-team workflow
- classify the request
- choose Fast Lane or Full Lane
- choose the starting role
- load relevant Skills
- run the workflow until human approval is needed

## Boundaries

AgentCrew does not replace OpenClaw runtime behavior.

AgentCrew must not override:

- OpenClaw identity instructions
- OpenClaw memory policy
- OpenClaw channel behavior
- OpenClaw heartbeat behavior
- OpenClaw gateway or device safety rules
- OpenClaw credential handling

If instructions conflict, preserve safety, privacy, and human approval.
