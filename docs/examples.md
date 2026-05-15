# Examples

## Example 1 — Small bug fix

### Prompt

```text
Act as Developer Agent.

Task:
Fix the login form so empty email shows a validation message.

Acceptance Criteria:
- empty email shows "Email is required"
- form does not submit when email is empty
- existing behavior remains unchanged

Use Fast Lane.
Keep the PR small.
```

### Expected flow

```text
Developer -> Tester -> Human
```

---

## Example 2 — New feature

### Prompt

```text
Act as Product Manager Agent.

Idea:
Users should be able to create projects from the dashboard.

Create small implementation tasks.
Use Fast Lane unless a task is risky.
```

### Expected output

```yaml
tasks:
  - add create project form
  - add project creation API call
  - add validation
  - add success/error states
```

---

## Example 3 — Risky auth change

### Prompt

```text
Act as Advisor Agent.

Idea:
Change how API tokens are validated.

Evaluate risk and recommend whether this should use Fast Lane or Full Lane.
```

### Expected lane

```yaml
lane: Full Lane
reason: authentication and security-sensitive behavior
```

---

## Example 4 — PR testing

### Prompt

```text
Act as Tester Agent.

Validate PR #12 against these acceptance criteria:
- project name is required
- duplicate project names return an error
- successful creation redirects to project page

Run relevant tests and produce a test report.
```

---

## Example 5 — Review with rework

### Prompt

```text
Act as Reviewer Agent.

Review PR #12.
If there are real issues, request rework using the review-report template.
```

### Possible finding

```yaml
finding:
  severity: high
  type: test_gap
  description: duplicate project name behavior is not covered by tests
  recommendation: add regression test
```

---

## Example 6 — Human change request

### Prompt

```text
Act as Developer Agent.

The human requested this PR change:
- rename "workspace" to "project" in user-facing labels only

Update the existing PR.
Do not change database names or internal model names.
```

---

## Example 7 — Escalation

### Prompt

```text
This task started as Fast Lane, but it now touches database migration and auth logic.

Reclassify the task using task-classification.md.
```

### Expected response

```yaml
risk: high
lane: Full Lane
reason:
  - touches auth
  - includes migration
  - rollback risk increased
```

Use:

```text
agent-team/playbooks/lane-escalation.md
```

---

## Example 8 — Security review

### Prompt

```text
Act as Security Reviewer Agent.

Review PR #18 for authentication, authorization, secret handling, and data exposure risk.
Use agent-team/templates/security-review-report.md.
```

Trigger specialist review using:

```text
agent-team/playbooks/specialist-review-routing.md
```

---

## Example 9 — UX / design review

### Prompt

```text
Act as UX / Design Reviewer Agent.

Review this checkout form change for usability, accessibility, responsive behavior, and visual clarity.
Use agent-team/templates/ux-design-review-report.md.
```

---

## Example 10 — Documentation update

### Prompt

```text
Act as Documentation Agent.

Update README and usage docs for this workflow change.
Use agent-team/templates/documentation-report.md.
```
