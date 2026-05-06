# Fast Lane Playbook

## Purpose

Fast Lane is the default startup development mode.

It minimizes ceremony while preserving enough quality control.

---

# 1. Use Fast Lane For

```yaml
use_for:
  - small features
  - bug fixes
  - experiments
  - MVP iterations
  - internal tools
  - low-risk UI changes
  - isolated backend endpoints
```

---

# 2. Do Not Use Fast Lane For

```yaml
do_not_use_for:
  - authentication
  - authorization
  - billing
  - data migrations
  - security-sensitive changes
  - infrastructure changes
  - large refactors
  - public API changes
```

---

# 3. Fast Lane Flow

```text
Human or PM task
  -> Developer Agent
  -> Tester Agent
  -> Optional Reviewer Agent
  -> Human approval
```

---

# 4. Fast Lane Rules

```yaml
rules:
  max_primary_agents: 3
  default_reviewer_required: false
  human_approval_required: true
  merge_by_agent_allowed: false
  pr_size: small
```

---

# 5. Fast Lane Task Shape

Good Fast Lane task:

```yaml
task:
  title: Add health endpoint
  risk: low
  scope: one endpoint
  acceptance_criteria:
    - GET /healthz returns 200
    - response includes status ok
```

Bad Fast Lane task:

```yaml
task:
  title: Redesign authentication system
  reason_bad: high risk and broad scope
```

---

# 6. Fast Lane Completion Criteria

A Fast Lane task is complete when:

```yaml
completion:
  - developer opened or updated PR
  - tester passed validation or documented limitations
  - reviewer checked if required
  - human approved
  - human merged
```
