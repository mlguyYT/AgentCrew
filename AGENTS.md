# Repository Agent Instructions

These instructions define how AI coding agents should work in this repository.

They are intentionally tool-agnostic.

Use them with Codex, Claude Code, Cursor, GitHub Copilot, Gemini, or any agent that can read repository instructions.

---

## Source of truth

The canonical agent workflow lives in:

```text
agent-team/
```

Read these files before performing work:

```text
agent-team/README.md
agent-team/playbooks/fast-lane.md
agent-team/playbooks/full-lane.md
agent-team/playbooks/pr-process.md
agent-team/playbooks/rework-loop.md
agent-team/playbooks/task-classification.md
agent-team/playbooks/lane-escalation.md
agent-team/playbooks/specialist-review-routing.md
agent-team/playbooks/skill-loading.md
agent-team/playbooks/skill-validation.md
agent-team/playbooks/memory-saving.md
agent-team/protocols/communication.md
agent-team/protocols/handoff-format.md
agent-team/protocols/state-artifacts.md
agent-team/protocols/token-discipline.md
```

Use agent-specific instructions from:

```text
agent-team/agents/
```

Use output templates from:

```text
agent-team/templates/
```

Use technical Skills from:

```text
agent-team/skills/registry.md
agent-team/skills/authoring-guide.md
```

Use policies and checklists from:

```text
agent-team/policies/
agent-team/checklists/
agent-team/conventions/
```

Use communication protocols from:

```text
agent-team/protocols/
```

---

## Default operating mode

Default to:

```yaml
mode: Fast Lane
```

Fast Lane means:

```text
Task
  -> Developer
  -> Tester
  -> Reviewer only if needed
  -> Specialist reviewer only if needed
  -> Human approval
```

Use Full Lane when the task is high risk.

---

## Default request routing

Users do not need to name a role, lane, or Skill.

When the user asks a normal question or requests an outcome, AgentCrew must:

```yaml
request_routing:
  - understand the requested outcome
  - classify risk using agent-team/playbooks/task-classification.md
  - choose Fast Lane or Full Lane
  - choose the starting role
  - load relevant Skills from agent-team/skills/registry.md
  - run the workflow until human approval is needed
```

Examples:

```text
"Fix this login validation bug" -> Developer -> Tester -> Human
"Plan this new dashboard feature" -> Product Manager -> Developer -> Tester -> Reviewer -> Human
"Change token validation" -> Advisor/Product Manager -> Developer -> Tester -> Reviewer -> Security Reviewer -> Human
```

If the user explicitly names a role, lane, or Skill, honor that unless it conflicts with safety rules or human approval.

---

## Non-negotiable rules

```yaml
rules:
  human_approval_required: true
  agents_may_merge: false
  agents_may_bypass_branch_protection: false
  agents_may_commit_secrets: false
  agents_may_hide_test_failures: false
  keep_prs_small: true
  avoid_unrelated_changes: true
```

---

## Human-only actions

Only the human may:

```yaml
human_only:
  - approve final product direction
  - approve backlog for large work
  - approve pull requests
  - merge pull requests
  - accept security or data-risk tradeoffs
  - override quality gates
```

---

## Agent roles

Use the following role files:

```yaml
roles:
  advisor: agent-team/agents/advisor.md
  idea_consultant: agent-team/agents/idea-consultant.md
  product_manager: agent-team/agents/product-manager.md
  developer: agent-team/agents/developer.md
  tester: agent-team/agents/tester.md
  reviewer: agent-team/agents/reviewer.md
  security_reviewer: agent-team/agents/security-reviewer.md
  ux_design_reviewer: agent-team/agents/ux-design-reviewer.md
  documentation_agent: agent-team/agents/documentation-agent.md
  skill_validator: agent-team/agents/skill-validator.md
```

If a role file is missing, create it before relying on that role.

---

## Task classification

Before starting work, classify the task:

```yaml
risk_levels:
  low:
    lane: Fast Lane
  medium:
    lane: Fast Lane or Full Lane
  high:
    lane: Full Lane
  critical:
    lane: Full Lane plus human decision
```

When unsure, choose the safer lane or ask the human.

---

## Skill loading

Before implementation, testing, or review, inspect the task and repository context for matching Skills.

Load Skills from:

```text
agent-team/skills/registry.md
```

Skills may be selected by:

```yaml
skill_inputs:
  - explicit Skills field
  - task text
  - labels
  - changed files
  - file extensions
  - dependency files
  - framework names
  - imports and code symbols
```

Skills improve execution quality but never override human approval, safety rules, or repository instructions.

For larger tasks, agents should include a short `## Skills Applied` note in their output when it helps the human understand which technical guidance was used.

When adding or changing Skills, use:

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
agent-team/templates/skill-validation-report.md
```

---

## Memory saving

When the human asks to save progress, when work pauses, or when a useful decision needs durable context, use:

```text
agent-team/playbooks/memory-saving.md
agent-team/templates/memory-summary.md
```

If the optional utility is available, save a local session checkpoint with:

```bash
~/AgentCrew/agent-team/tools/save-session.sh --project . --title "short title"
```

Memory must not include secrets, raw customer data, sensitive production data, or large logs.

Do not store project memory inside `agent-team/`; that folder is the reusable workflow package.

---

## Communication protocol

Agents must communicate through compact artifacts instead of long chat when handing work to another agent.

Default handoff format:

```md
### Context
1-3 bullets only.

### Decision
What was decided.

### Evidence
Only the facts needed by the next agent.

### Next Action
Exactly what the next agent should do.

### Open Questions
Only blockers.
```

Use:

```text
agent-team/protocols/communication.md
agent-team/protocols/handoff-format.md
agent-team/protocols/state-artifacts.md
agent-team/protocols/token-discipline.md
```

Agents do not pass full reasoning. Agents pass compact artifacts.

Preferred shared project artifacts:

```text
.agent-state/sessions/
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

Do not store secrets, raw customer data, sensitive production data, or long logs in shared artifacts.

---

## PR rules

All PRs should be:

```yaml
pr_rules:
  - small
  - focused
  - linked to a task
  - tested or clearly marked as not tested
  - modular and aligned with clean architecture for scalable maintenance
  - code coverage is at least 70 percent when coverage tooling exists
  - reviewed before human approval
```

Never include unrelated refactors unless explicitly requested.

---

## Rework routing

If Tester, Reviewer, Security Reviewer, UX / Design Reviewer, Documentation Agent, CI, or Human requests changes:

```text
Route implementation rework back to the Developer.
Use the same PR branch unless told otherwise.
```

---

## Done definition

Work is done only when:

```yaml
done:
  - task objective is satisfied
  - acceptance criteria are addressed
  - implementation remains modular and consistent with project architecture
  - relevant tests are run or limitations documented
  - test coverage is at least 70 percent when coverage tooling exists, or the gap is documented for human decision
  - PR description is clear
  - reviewer concerns are resolved or documented
  - human approves final merge
```

---

## Output expectations

Use templates from:

```text
agent-team/templates/
```

For example:

```yaml
developer:
  use: agent-team/templates/pr-description.md

tester:
  use: agent-team/templates/test-report.md

reviewer:
  use: agent-team/templates/review-report.md

security_reviewer:
  use: agent-team/templates/security-review-report.md

ux_design_reviewer:
  use: agent-team/templates/ux-design-review-report.md

documentation_agent:
  use: agent-team/templates/documentation-report.md

product_manager:
  use: agent-team/templates/task.md

skill_validator:
  use: agent-team/templates/skill-validation-report.md

memory_saving:
  use: agent-team/templates/memory-summary.md
```

---

## Conflict resolution

If instructions conflict:

1. safety rules win
2. human instructions win
3. repository-specific instructions win
4. agent-team instructions apply next
5. role-specific instructions apply next

Never interpret conflict as permission to bypass human approval.
