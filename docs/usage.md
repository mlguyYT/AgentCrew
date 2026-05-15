# Usage Guide

## Purpose

This guide explains how to use the AgentCrew workflow in day-to-day development.

---

## Basic usage

Use natural language with your coding agent.

Example:

```text
Read AGENTS.md and the agent-team folder.

Use Fast Lane by default.
Use Full Lane for risky work.
Do not merge pull requests.
Keep PRs small.
Route implementation rework back to the Developer.
Load relevant Skills automatically from agent-team/skills/registry.md.
Keep handoffs compact using the communication protocol.
```

---

## Choose the right role

Use these prompts.

### Advisor

```text
Act as the Advisor Agent.
Evaluate this idea and tell me whether to proceed, refine, or reject.
Keep the advice practical and startup-focused.
```

### Idea Consultant

```text
Act as the Idea Consultant Agent.
Turn this raw idea into an idea brief using agent-team/templates/idea-brief.md.
```

### Product Manager

```text
Act as the Product Manager Agent.
Turn this idea brief into small implementation tasks.
Use agent-team/templates/task.md.
Classify risk and recommend Fast Lane or Full Lane.
```

### Developer

```text
Act as the Developer Agent.
Implement this task.
Keep the PR small.
Follow agent-team/playbooks/pr-process.md.
```

### Tester

```text
Act as the Tester Agent.
Validate this branch against the acceptance criteria.
Use agent-team/templates/test-report.md.
```

### Reviewer

```text
Act as the Reviewer Agent.
Review this PR for correctness, scope, maintainability, tests, and risk.
Use agent-team/templates/review-report.md.
```

### Security Reviewer

```text
Act as the Security Reviewer Agent.
Review this PR for auth, permissions, secrets, data handling, dependency, and infrastructure risk.
Use agent-team/templates/security-review-report.md.
```

### UX / Design Reviewer

```text
Act as the UX / Design Reviewer Agent.
Review this user-facing change for usability, accessibility, responsive behavior, and visual quality.
Use agent-team/templates/ux-design-review-report.md.
```

### Documentation Agent

```text
Act as the Documentation Agent.
Review and update docs, examples, changelog, or release notes affected by this change.
Use agent-team/templates/documentation-report.md.
```

### Skill Validator

```text
Act as the Skill Validator Agent.
Validate this Skill using agent-team/playbooks/skill-validation.md.
Use agent-team/templates/skill-validation-report.md.
```

---

## Default workflow

For most small work:

```text
Task
  -> Developer
  -> Tester
  -> Reviewer only if needed
  -> Human approval
```

If risk is medium:

```text
Task
  -> Developer
  -> Tester
  -> Reviewer
  -> Human approval
```

If risk is high:

```text
Idea
  -> Advisor
  -> Idea Consultant
  -> Product Manager
  -> Human concept approval
  -> Product Manager backlog planning
  -> Human backlog approval
  -> Developer
  -> Tester
  -> Reviewer
  -> Specialist Reviewer if needed
  -> Human PR approval
```

Use specialist reviewers only when their area is touched:

```text
Security Reviewer: security, privacy, data, auth, secrets, dependency or infrastructure risk
UX / Design Reviewer: UI, UX, accessibility, responsive behavior, visual quality
Documentation Agent: docs, examples, changelog, release notes
```

For explicit trigger rules, use:

```text
agent-team/playbooks/specialist-review-routing.md
```

---

## How to classify a task

Ask:

```text
Classify this task using agent-team/playbooks/task-classification.md.
Should it use Fast Lane or Full Lane?
```

The agent should return:

```yaml
risk: low | medium | high | critical
lane: Fast Lane | Full Lane
reason: explanation
```

If risk changes during work, use:

```text
agent-team/playbooks/lane-escalation.md
```

---

## How Skills are selected

Agents should load Skills automatically from:

```text
agent-team/skills/registry.md
```

Skills may be triggered by task text, explicit `Skills` fields, changed files, dependency files, imports, or framework names.

Example:

```md
## Skills
- python-pro
- fastapi
```

---

## How to validate a Skill

Ask:

```text
Act as Skill Validator Agent.
Validate agent-team/skills/frameworks/example.md.
Check registry path, triggers, safety rules, testing guidance, and overlap with existing Skills.
```

The agent should return a recommendation:

```yaml
recommendation: valid | valid_with_notes | rework_required | reject
```

When creating a Skill, use:

```text
agent-team/skills/authoring-guide.md
```

---

## How to save memory

Ask:

```text
Save memory for this work using agent-team/playbooks/memory-saving.md.
Use agent-team/templates/memory-summary.md.
Do not include secrets, raw customer data, or large logs.
```

For committed project memory, prefer a project-owned path such as:

```text
docs/agent-memory/
```

Do not save project memory inside `agent-team/`.

Use `.agent-state/` for active handoff state. Use durable memory only for decisions or context worth preserving beyond the current task.

---

## How to request a PR

Example:

```text
Act as Developer Agent.

Task:
Add a `/healthz` endpoint that returns `{ "status": "ok" }`.

Acceptance Criteria:
- GET /healthz returns HTTP 200
- response body includes status ok
- include a simple test if the project has test infrastructure

Use Fast Lane.
Do not modify unrelated files.
```

---

## How to request testing

Example:

```text
Act as Tester Agent.

Validate the current branch.

Acceptance Criteria:
- GET /healthz returns HTTP 200
- response body includes status ok

Run relevant tests.
If tests cannot be run, explain why.
Use the test-report template.
```

---

## How to request review

Example:

```text
Act as Reviewer Agent.

Review this PR.

Focus on:
- correctness
- scope control
- maintainability
- test adequacy

Do not nitpick.
Only request changes for meaningful issues.
```

---

## How to handle rework

Example:

```text
Act as Developer Agent.

Address this rework request:
- The endpoint should return JSON, not plain text.
- Add a test for the response body.

Update the existing PR.
Do not expand scope.
```

---

## How agents should hand off work

Use compact artifacts instead of long chat:

```text
agent-team/protocols/communication.md
agent-team/protocols/handoff-format.md
agent-team/protocols/token-discipline.md
agent-team/protocols/state-artifacts.md
```

Ask:

```text
Create a PM -> Developer handoff using agent-team/protocols/handoff-format.md.
Keep it under 200 words.
```

Recommended shared artifacts:

```text
.agent-state/current-task.md
.agent-state/decisions.md
.agent-state/handoff.md
.agent-state/test-report.md
.agent-state/review-report.md
.agent-state/security-review-report.md
.agent-state/ux-design-review-report.md
.agent-state/documentation-report.md
.agent-state/memory.md
```

Use `agent-team/protocols/state-artifacts.md` for the standard schema.

The `agent-team/` folder contains reusable methodology.
The `.agent-state/` folder contains current project state.

Do not store secrets, tokens, raw customer data, or large logs in `.agent-state/`.

---

## Human approval

Even if agents say work is ready, the human must decide:

```yaml
human_decision:
  - approve
  - request changes
  - reject
  - split task
  - pause
```

---

## Best practices

```yaml
best_practices:
  - keep tasks small
  - use Fast Lane by default
  - escalate only when risk appears
  - ask PM to split vague work
  - ask Tester for evidence
  - ask Reviewer for meaningful risks
  - keep human approval final
```
