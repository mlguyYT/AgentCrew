# Agent Lifecycle Playbook

## Purpose

This document defines how to create, scale, disable, and delete agents and subagents.

---

# 1. Agent Registry Model

Every agent should be registered with:

```json
{
  "role": "developer",
  "specialization": "backend",
  "capacity": 1,
  "execution_profile": {
    "mode": "implementation",
    "default_image": "agent-platform/base-worker:dev"
  }
}
```

Required fields:

```yaml
required:
  - role
  - capacity
  - execution_profile
```

Optional:

```yaml
optional:
  - specialization
```

---

# 2. Create Agent

Create an agent when:

```yaml
create_when:
  - new role is needed
  - specialization is needed
  - queue is too long
  - existing agent is overloaded
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "role": "developer",
    "specialization": "backend",
    "capacity": 1,
    "execution_profile": {
      "mode": "implementation",
      "default_image": "agent-platform/base-worker:dev"
    }
  }'
```

---

# 3. Scale Agent

Scale by adding more registered agents or increasing allowed runtime concurrency.

Do not scale by allowing multiple developers to edit the same branch unless explicitly assigned.

```yaml
safe_scaling:
  - more independent tasks
  - more specialized agents
  - more worker jobs

unsafe_scaling:
  - multiple agents pushing to same PR branch
  - unclear ownership
  - no reviewer/tester capacity
```

---

# 4. Disable Agent

Disable an agent when:

```yaml
disable_when:
  - replacing with better specialization
  - reducing local resource usage
  - agent is misconfigured
  - agent is not needed
```

Safe disable procedure:

```text
1. mark disabled
2. stop assigning new tasks
3. wait for active tasks to complete
4. reassign unfinished tasks
5. preserve logs/artifacts
```

---

# 5. Delete Agent

Hard delete only when:

```yaml
delete_allowed_if:
  - no active tasks
  - no active PR ownership
  - no pending rework
  - artifacts preserved
```

Never delete an agent that owns active PRs.

---

# 6. Recommended Initial Agents

```yaml
initial_agents:
  - role: advisor
    specialization: startup

  - role: idea_consultant
    specialization: startup

  - role: product_manager
    specialization: technical

  - role: developer
    specialization: backend

  - role: tester
    specialization: regression

  - role: reviewer
    specialization: code

  - role: security_reviewer
    specialization: application_security

  - role: ux_design_reviewer
    specialization: product_ui

  - role: documentation_agent
    specialization: product_docs
```
