# Rework Loop Playbook

## Purpose

This playbook defines how failed work returns to the right agent.

A good rework loop keeps development fast and prevents confusion.

---

## Core rule

```text
Implementation rework returns to the original Developer Agent owner.
```

The original Developer should update the same PR branch unless instructed otherwise.

---

## Rework sources

Rework may come from:

```yaml
sources:
  - Tester Agent
  - Reviewer Agent
  - Human
  - CI failure
  - build failure
  - production feedback
```

---

## Tester rework

Flow:

```text
Tester finds failure
  -> writes test report
  -> requests rework
  -> Developer updates PR
  -> Tester validates again
```

Tester rework request should include:

```yaml
tester_rework:
  - failed acceptance criterion
  - command run
  - failure output
  - expected behavior
  - actual behavior
  - suggested next step
```

---

## Reviewer rework

Flow:

```text
Reviewer finds issue
  -> writes review report
  -> requests rework
  -> Developer updates PR
  -> Tester re-validates if behavior changed
  -> Reviewer reviews again
```

Reviewer rework should include:

```yaml
reviewer_rework:
  - finding type
  - severity
  - affected files
  - explanation
  - suggested fix
```

---

## Human rework

Human may request:

```yaml
human_rework_routes:
  developer:
    when: implementation change needed
  tester:
    when: more validation needed
  reviewer:
    when: more review needed
  product_manager:
    when: scope changed
  idea_consultant:
    when: concept changed
```

---

## CI failure rework

Flow:

```text
CI fails
  -> Tester or CI Execution Agent classifies failure
  -> Developer fixes if code-related
  -> Tester validates
```

If failure is environment-related, route to human or infra specialist.

---

## Rework count

Track repeated rework.

Recommended policy:

```yaml
rework_policy:
  soft_limit: 3
  after_soft_limit: require_human_decision
```

If a PR has too many rework loops, consider:

```yaml
possible_actions:
  - split PR
  - revise task
  - send back to PM
  - ask human for direction
  - abandon and restart
```

---

## Rework request template

```md
## Rework Request

### Source
Tester / Reviewer / Human / CI

### Reason
Why rework is required.

### Required Changes
- change 1
- change 2

### Evidence
Command output, review comment, or failing criterion.

### Route
Return to original Developer Agent.
```

---

## Rework completion criteria

Rework is complete when:

```yaml
complete:
  - requested changes addressed
  - tests rerun if needed
  - PR updated
  - response comment added
  - original requester can re-check
```

---

## Agent instruction

When handling rework:

```text
Stay focused.
Fix only requested issues.
Do not expand scope.
Use the same PR branch.
Report what changed.
```
