# Workflow: PR → Review → Approval

## Purpose
Ensure PR quality before merge.

---

## Flow

```text
PR
  -> Tester
  -> Reviewer (optional or required)
  -> Human approval
```

---

## Step 1 — Tester validation

Tester:
- runs tests
- checks acceptance criteria

Uses:
agent-team/templates/test-report.md

---

## Step 2 — Reviewer review

Reviewer checks:
- correctness
- scope
- maintainability
- risks

Uses:
agent-team/templates/review-report.md

---

## Step 3 — Human approval

Human:
- reviews PR
- approves or requests changes
- merges

---

## Output

```yaml
output:
  - test report
  - review report
  - human decision
```
