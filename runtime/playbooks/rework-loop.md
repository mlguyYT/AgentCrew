# Rework Loop Playbook

## Purpose

This document defines how failed PRs, reviewer comments, tester failures, and human change requests are routed.

---

# 1. Core Rule

All implementation rework goes back to the original Developer Agent owner.

```text
original developer owner remains responsible until PR is merged or abandoned
```

---

# 2. Tester Failure

```text
Tester Agent
  -> rework_required
  -> Orchestrator
  -> Developer Agent owner
  -> Same PR branch
```

Payload:

```json
{
  "source": "tester",
  "reason": "Acceptance criterion failed",
  "route_to": "original_developer_owner"
}
```

---

# 3. Reviewer Change Request

```text
Reviewer Agent
  -> rework_required
  -> Orchestrator
  -> Developer Agent owner
  -> Same PR branch
  -> Tester again
  -> Reviewer again
```

---

# 4. Human Change Request

Human can route to:

```yaml
route_options:
  developer:
    when: implementation change needed
  reviewer:
    when: more review needed
  product_manager:
    when: scope or acceptance criteria changed
```

---

# 5. CI Failure

```text
GitHub CI failure
  -> GitHub Integration
  -> Orchestrator
  -> Tester or CI Execution Agent
  -> Developer if code failure
```

---

# 6. Rework Count

Track rework count.

```yaml
rework_policy:
  max_soft_rework_count: 3
  after_soft_limit: human_decision_required
```

If the same PR loops too much, escalate to human.

---

# 7. Rework Completion

After rework:

```text
Developer updates PR
  -> Tester validates
  -> Reviewer checks if required
  -> Human approval
```
