# Examples

Before using these examples, install and register AgentCrew once:

```bash
git clone https://github.com/mlguyYT/AgentCrew.git ~/AgentCrew
~/AgentCrew/bin/agentcrew install
```

After that, open any project and enjoy development with your AgentCrew.

Paths in these examples are relative to the external AgentCrew checkout unless a project path is explicitly named.

---

## Example 1 — Small bug fix

### Prompt

```text
Fix the login form so empty email shows a validation message.

Acceptance Criteria:
- empty email shows "Email is required"
- form does not submit when email is empty
- existing behavior remains unchanged

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
Users should be able to create projects from the dashboard.

Plan the work, split it into small implementation tasks, and choose the right lane for each task.
```

### Expected routing and output

```text
Product Manager -> Developer -> Tester -> Reviewer if needed -> Human
```

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
Change how API tokens are validated.

Evaluate risk, choose the right AgentCrew lane, and identify required reviewers.
```

### Expected routing

```yaml
lane: Full Lane
reason: authentication and security-sensitive behavior
specialist_review:
  - Security Reviewer
```

---

## Example 4 — PR testing

### Prompt

```text
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
Review this checkout form change for usability, accessibility, responsive behavior, and visual clarity.
Use agent-team/templates/ux-design-review-report.md.
```

---

## Example 10 — Documentation update

### Prompt

```text
Update README and usage docs for this workflow change.
Use agent-team/templates/documentation-report.md.
```
