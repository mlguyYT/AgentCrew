# Codex Implementation Guide

## Purpose

This document tells Codex how to use the agent documentation to create or modify the implementation.

---

# 1. Folder Structure

Expected structure:

```text
runtime/
  agents/
  advisor.md
  idea-consultant.md
  product-manager.md
  developer.md
  tester.md
  reviewer.md
  ci-execution.md

  coordinator/
    agent-coordinator.md

  integrations/
    github.md

  playbooks/
    master-workflow.md
    fast-lane.md
    full-lane.md
    agent-lifecycle.md
    rework-loop.md
    local-ubuntu-runtime.md
    codex-implementation-guide.md
```

---

# 2. Implementation Priority

Codex should implement in this order:

```yaml
implementation_order:
  1: core models
  2: orchestrator transitions
  3: agent registry
  4: coordinator job launcher
  5: worker envelope
  6: GitHub integration
  7: rework routing
  8: local deployment scripts
  9: OpenClaw runtime placeholders
  10: CI execution support
```

---

# 3. Non-Negotiable Rules

Codex must not implement:

```yaml
forbidden:
  - autonomous merge
  - branch protection bypass
  - secret logging
  - direct pushes to protected branch
  - skipping human approval gates
```

---

# 4. Required System Behaviors

Codex must ensure:

```yaml
required:
  - developer owns PR
  - tester can request rework
  - reviewer can request rework
  - human approves PR
  - orchestrator blocks invalid transitions
  - coordinator launches isolated workers
  - GitHub events map to workflow events
  - placeholders exist for user-owned values
```

---

# 5. Adding New Subagents

To add a new subagent:

1. create agent registration
2. assign role
3. assign specialization
4. define execution profile
5. map runtime profile in coordinator
6. define permissions
7. define deletion safety rules

Example:

```json
{
  "role": "developer",
  "specialization": "frontend",
  "capacity": 1,
  "execution_profile": {
    "mode": "frontend_implementation",
    "default_image": "agent-platform/base-worker:dev"
  }
}
```

---

# 6. Deleting Subagents

Before deletion, Codex must verify:

```yaml
checks:
  - no active task
  - no active PR ownership
  - no pending rework
  - logs preserved
```

If checks fail, disable but do not delete.

---

# 7. Final Acceptance Criteria

The system is acceptable when:

```yaml
acceptance:
  - docs exist for every agent
  - docs define create/scale/delete behavior
  - docs define workflow routes
  - docs define local runtime
  - docs define GitHub integration
  - docs define coordinator runtime
  - docs define startup fast/full lane behavior
```
