# Usage Guide

## Purpose

This guide explains how to use the AgentCrew workflow in day-to-day development.

---

## Token-safe loading

AgentCrew routes first and loads details only when needed. Normal work should start from:

```text
AGENTS.md
agent-team/context/route-index.md
```

Then the agent should load one context profile, one role file, matching Skills, triggered gates, and the current output template. Do not load every AgentCrew file for small tasks.

---

## Basic usage

Use natural language with your coding agent.

Example:

```text
Fix the login form so empty email shows a validation message.
```

After one-time registration, AgentCrew should be loaded automatically. It should read its own instructions, classify the task, choose the lane, role, and Skills, and stop where human approval is required.

Add extra rules to your prompt only when you want to constrain or override the default workflow.

Paths in the examples below are relative to the external AgentCrew checkout unless a project path is explicitly named.

If automatic loading has not been registered yet, run:

```bash
~/AgentCrew/bin/agentcrew install
~/AgentCrew/bin/agentcrew doctor
```


## Project detection

Use the detector when you want a quick read-only profile of a project before routing work:

```bash
~/AgentCrew/bin/agentcrew detect-project --project .
```

The profile lists likely languages, frameworks, package managers, validation commands, coverage hints, and suggested Skills. Agents should use it as a starting point and still inspect the task-specific files.

---

## Automatic routing

You do not need to choose the role, lane, or Skill.

AgentCrew should infer them from the request:

```text
"Fix the login validation bug"
  -> Developer -> Tester -> Human, with Reviewer/PM if risk or behavior scope requires it

"Plan a project creation feature"
  -> Product Manager -> Developer -> Tester -> Reviewer -> Human

"Change how API tokens are validated"
  -> Advisor -> Product Manager -> Developer -> Tester -> Reviewer -> Security Reviewer -> Human

"Review this checkout form change"
  -> UX / Design Reviewer -> Human
```

Explicit role prompts are optional. Use them when you want manual control or when an agent ignores routing.

---

## Optional manual role prompts

Use these prompts only when you want to force a specific role.

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

### LLM Agent

```text
Act as the LLM Agent.
Review this prompt, RAG, tool-calling, model behavior, eval coverage, and LLM safety risk.
Use agent-team/templates/llm-report.md.
```

### Researcher Agent

```text
Act as the Researcher Agent.
Research this question with source-backed evidence, separate facts from assumptions, state confidence, and list open questions.
Use agent-team/templates/research-report.md.
```

### CNN Agent

```text
Act as the CNN Agent.
Review this computer vision or CNN work for dataset quality, leakage, metrics, overfitting, reproducibility, and inference constraints.
Use agent-team/templates/cnn-report.md.
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
  -> Reviewer when risk is meaningful
  -> Product Manager when scope or product behavior changes
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
LLM Agent: prompts, RAG, evals, model behavior, tool use, LLM safety
Researcher Agent: source-backed research, current information, comparisons, uncertainty
CNN Agent: computer vision, CNNs, image datasets, training, evaluation, inference
```

For explicit trigger rules, use:

```text
agent-team/playbooks/specialist-review-routing.md
```

---

## How to classify a task

Classification is automatic by default. Ask explicitly only when you want the routing decision before work starts:

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
Validate agent-team/skills/frameworks/fastapi.md.
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

Or save a local session checkpoint from the target project:

```bash
~/AgentCrew/agent-team/tools/save-session.sh --project . --title "short title"
```

List saved sessions or show the latest checkpoint:

```bash
~/AgentCrew/agent-team/tools/list-sessions.sh --project .
~/AgentCrew/agent-team/tools/list-sessions.sh --project . --latest
```

The checkpoint is saved under the target project's own `.agent-state/sessions/`.
If you run the command from a subdirectory, AgentCrew resolves the git repository root automatically.

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
Add a `/healthz` endpoint that returns `{ "status": "ok" }`.

Acceptance Criteria:
- GET /healthz returns HTTP 200
- response body includes status ok
- include a simple test if the project has test infrastructure

Classify the task and use the right AgentCrew lane, role, and Skills.
Do not modify unrelated files.
```

---

## How to request testing

Example:

```text
Validate the current branch.

Acceptance Criteria:
- GET /healthz returns HTTP 200
- response body includes status ok

Run relevant tests.
If tests cannot be run, explain why.
Use the AgentCrew test-report template.
```

---

## How to request review

Example:

```text
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
