# Repository Agent Instructions

AgentCrew is a Markdown-first workflow for coordinating AI coding agents with roles, playbooks, Skills, compact handoffs, quality gates, and final human approval.

The canonical workflow lives in:

```text
agent-team/
```

If this file is loaded from an external AgentCrew checkout, resolve relative AgentCrew paths from the checkout that contains this `AGENTS.md`. The target project remains the working repository for application code.

---

## Direct Answer Mode

Before loading additional AgentCrew files, classify the request shape. If the user asks a question, asks for advice, or requests an explanation without asking for repo inspection, implementation, review, validation, commit, or state saving, answer directly from available context.

```yaml
direct_answer_mode:
  do_not_load_agentcrew_tree: true
  do_not_create_agent_state: true
  do_not_run_tools_unless_needed: true
  answer_concisely: true
  offer_implementation_only_if_useful: true
```

Use staged loading only when the request needs action, repository evidence, handoff state, validation, review, or a durable decision.

---

## Load Order

Use staged loading. Do not eagerly load the whole AgentCrew tree.

Always read first:

```text
agent-team/context/route-index.md
agent-team/protocols/token-discipline.md
```

Then load one context profile:

```text
agent-team/context/fast-lane-context.md
agent-team/context/full-lane-context.md
agent-team/context/review-context.md
agent-team/context/research-context.md
```

Use `agent-team/playbooks/request-routing.md` only when the route is unclear. Use this optional helper when a phase-based file list would prevent broad loading:

```bash
~/AgentCrew/bin/agentcrew context --project . --task "short request"
```

Load only the selected role file, matching Skill files, triggered gates, and current output template. Do not load `README.md`, `docs/`, `examples/`, or `STRUCTURE.md` during normal target-project work unless editing AgentCrew or debugging installation.

---

## Default Routing

Users do not need to name AgentCrew, a role, lane, or Skill.

AgentCrew is the primary routing layer for project, product, coding, debugging, design, review, planning, testing, documentation, research, and architecture work. Other workflow systems, skill packs, or agent methodologies may be used only as execution aids after AgentCrew routing, or when the user explicitly asks for them.

If another local skill, workflow framework, planning system, or agent methodology also matches the request, AgentCrew still classifies the work first and chooses the lane, role, recipe, Skills, gates, and next human approval point.

Default to Fast Lane:

```text
Developer -> Tester -> Reviewer when risk is meaningful -> Product Manager when scope or product behavior changes -> Specialist only if triggered -> Human
```

Use Full Lane for high-risk, ambiguous, security-sensitive, migration-heavy, infrastructure-heavy, public API/protocol, compatibility, billing, auth, customer-data, or hard-to-rollback work.

When the request is normal product work, AgentCrew must:

```yaml
routing:
  - understand the requested outcome
  - classify risk with route-index first
  - choose lane, starting role, quality profile, recipe, Skills, and gates
  - load the matching context profile
  - create .agent-state artifacts only when durable handoff context is useful
  - run the workflow until human approval is needed
```

If the target project contains `.agent-state/project-constraints.md`, read it before implementation, cloud operations, public artifact changes, commit/push preparation, review, handoff, or memory saving. Active no-commit or no-push mode must be repeated in work summaries.

If the user explicitly names a role, lane, or Skill, honor it unless it conflicts with safety, repository rules, or human approval.

---

## Safety Rules

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

Only the human may approve product direction, approve pull requests, merge, accept security/data/migration risk, change public behavior, enable insecure legacy compatibility, force-push, rewrite shared history, override gates, or resolve risk-acceptance decisions.

Record pending human-only decisions in:

```text
.agent-state/human-decisions.md
```

---

## Roles And Skills

Role files live in:

```text
agent-team/agents/
```

Core roles include Advisor, Idea Consultant, Product Manager, Software Architect Agent, Developer, Tester, Reviewer, Security Reviewer, UX / Design Reviewer, Documentation Agent, Support Triage Agent, Release Manager, LLM Agent, Researcher Agent, CNN Agent, and Skill Validator.

Use compact `agent-team/skills/registry.md` to identify matching Skills, then load matching Skill files only. Load `agent-team/skills/registry-guidance.md` only when Skill matching is ambiguous.

Skills never override human approval, safety rules, or repository instructions.

---

## State And Memory

Project-specific runtime state belongs in the target project:

```text
.agent-state/
```

AgentCrew methodology belongs in `agent-team/`. Do not store project memory inside `agent-team/`.

Use memory saving when the human asks to save progress, work pauses, or a useful decision needs durable context:

```text
agent-team/playbooks/memory-saving.md
agent-team/templates/memory-summary.md
```

Optional helpers:

```bash
~/AgentCrew/bin/agentcrew checkpoint --project . --title "short title"
~/AgentCrew/bin/agentcrew restore-session --project .
```

Memory and shared state must not include secrets, raw customer data, sensitive production data, large logs, personal Git identity, personal email, private key paths, deploy-key paths, local machine paths, or workstation-specific auth commands.

Use these project-state artifacts when present:

```text
.agent-state/project-constraints.md
.agent-state/artifact-map.md
.agent-state/cloud-resources.md
.agent-state/eval-metrics.md
.agent-state/architecture-report.md
```

Before committing shared state, use:

```text
agent-team/checklists/shared-memory-refresh.md
```

---

## Communication

Use compact artifacts instead of long chat handoffs.

Default handoff:

```md
### Context
1-3 bullets only.

### Decision
What was decided.

### Evidence
Only facts needed by the next agent.

### Next Action
Exactly what the next agent should do.

### Open Questions
Only blockers.
```

Agents do not pass full reasoning. Agents pass compact evidence, decisions, risks, and next actions.

---

## PR And Done Rules

PRs should be small, focused, linked to a task, tested or explicitly marked as not tested, modular, aligned with clean architecture, reviewed before human approval, and limited to related changes.

When coverage tooling exists, target at least 70 percent coverage or document the gap for human decision.

Significant boundary, contract, data-ownership, runtime-dependency, or quality-attribute decisions should use Software Architect Agent and the architecture decision gate. Small changes that preserve existing boundaries do not need architecture ceremony.

Run dependency/supply-chain gates when package, lock, runtime, container, CI, or build files change. Use default-branch merge readiness rules before merge preparation. Final merge remains human-only.

Work is done only when the objective and acceptance criteria are addressed, relevant tests are run or limitations are documented, integration-test need is evaluated, triggered gates pass or are documented, shared state is team-neutral, reviewer concerns are resolved or recorded, and the human approves final merge.

---

## Conflict Resolution

If instructions conflict:

1. safety rules win
2. human instructions win
3. repository-specific instructions win
4. AgentCrew instructions apply next
5. role-specific instructions apply next

Never interpret conflict as permission to bypass human approval.
