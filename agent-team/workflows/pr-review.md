# Workflow: PR → Review → Approval

## Purpose
Ensure PR quality before merge.

---

## Flow

```text
PR
  -> Tester
  -> Reviewer (optional or required)
  -> Specialist Reviewer if needed
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

## Step 3 — Specialist review if needed

Use specialist reviewers when the PR touches their area:

- Security Reviewer: `agent-team/templates/security-review-report.md`
- UX / Design Reviewer: `agent-team/templates/ux-design-review-report.md`
- Documentation Agent: `agent-team/templates/documentation-report.md`

---

## Step 4 — Human approval

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
  - specialist report if required
  - human decision
```
