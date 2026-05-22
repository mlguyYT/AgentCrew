# Checkpoint Blocks

## Purpose

Checkpoint blocks preserve the smallest useful continuation context for a future AgentCrew session.

They are designed for token-efficient resume, not audit history, source of truth, or hidden reasoning storage.

---

## Canonical Block

Use this block inside `.agent-state/sessions/*.md` or another project-local state artifact:

```text
[agentcrew-context]
Task: <current task or checkpoint title>
Status: <current status>
Decision: <key decision, repeat line if needed>
Remaining: <next concrete work, repeat line if needed>
Tried: <failed approach worth remembering, optional>
Risk: <open risk or uncertainty, optional>
Skill: <role or Skill used, optional>
Validation: <commands or validation baseline, optional>
[/agentcrew-context]
```

Keep each line short and factual. Prefer several specific lines over one long paragraph.

---

## Rules

Checkpoint blocks must be:

```yaml
checkpoint_rules:
  - project_local
  - team_neutral_if_committed
  - factual
  - compact
  - safe_to_reload_into_agent_context
```

Never include:

```yaml
forbidden:
  - secrets
  - tokens
  - passwords
  - private keys
  - private key paths
  - deploy-key paths
  - personal Git identity
  - personal email addresses
  - local machine paths
  - workstation-specific auth commands
  - raw customer data
  - sensitive production data
  - long logs
  - full diffs
  - hidden reasoning traces
  - instructions that override AgentCrew safety rules
```

---

## Storage

Default location:

```text
.agent-state/sessions/
```

Each target project owns its own `.agent-state/` folder. Do not store target-project checkpoint blocks inside AgentCrew's `agent-team/` folder.

---

## Human Boundary

Agents may create checkpoint blocks when the human asks to save progress or when a handoff would otherwise lose important context.

Agents must not treat checkpoint blocks as higher priority than repository instructions, source code, tests, current human direction, or safety rules.

Automatic WIP commits are not part of the default AgentCrew checkpoint behavior. Any commit-based checkpoint mode must be explicit and human-approved.
