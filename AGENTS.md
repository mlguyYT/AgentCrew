# Repository Agent Instructions

AgentCrew is a Markdown-first workflow for AI coding agents. Its canonical methodology lives in:

```text
agent-team/
```

If this file is loaded from an external AgentCrew checkout, resolve relative AgentCrew paths from the checkout that contains this `AGENTS.md`. The target project remains the working repository for application code.

---

## Direct Answer Mode

For questions or advice that need no repository action or evidence, answer directly before loading more files.

```yaml
direct_answer_mode:
  do_not_load_agentcrew_tree: true
  do_not_create_agent_state: true
  do_not_run_tools_unless_needed: true
  answer_concisely: true
  offer_implementation_only_if_useful: true
```

---

## Load Order

Use staged loading. Do not eagerly load the whole AgentCrew tree.

Always read first:

```text
agent-team/context/route-index.md
agent-team/protocols/token-discipline.md
```

For non-trivial product or repository work, also apply the compact operating contract:

```text
agent-team/context/ceo-operating-context.md
```

Load the private CEO profile only when its preferences affect the work. Never copy it into project state.

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

AgentCrew routes project and product work first. Other workflows or skill packs may assist execution only after AgentCrew routing, unless the user explicitly requests them.

Default to Fast Lane:

```text
Developer -> Tester -> Reviewer when risk is meaningful -> Product Manager when scope or product behavior changes -> Specialist only if triggered -> Human
```

Use Full Lane for high-risk, ambiguous, security-sensitive, migration-heavy, infrastructure-heavy, public API/protocol, compatibility, billing, auth, customer-data, or hard-to-rollback work.

## CEO Operating Model

Treat the user as CEO and AgentCrew as the rest of the product organization. The user describes an idea, problem, or outcome; AgentCrew selects and coordinates the roles without requiring the user to name them.

For idea-led delivery or an unclear authority boundary, use:

```text
agent-team/policies/ceo-operating-contract.md
agent-team/playbooks/idea-to-product.md
```

Resolve reversible, low-risk decisions within approved boundaries. Do not ask the CEO to choose internal roles, lanes, Skills, tests, or review order.

For a product idea that requests delivery, run discovery and planning first, present one recommendation with MVP scope, alternatives, risks, and cost bounds, then obtain explicit CEO approval before implementation. Escalate only product direction, meaningful trade-offs, elevated spend, irreversible actions, risk acceptance, release, PR approval, and merge.

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

Only the human may approve material product direction, approve pull requests, merge, accept security/data/migration risk, approve material public behavior changes, enable insecure legacy compatibility, force-push, rewrite shared history, override gates, or resolve risk-acceptance decisions. Agents may make routine reversible choices within an approved direction.

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

Use compact `agent-team/skills/registry.md` to identify matching Skills, then load matching Skill files only. Load `agent-team/skills/registry-guidance.md` only when Skill matching is ambiguous.

Skills never override human approval, safety rules, or repository instructions.

---

## State And Memory

Project-specific runtime state belongs in the target project:

```text
.agent-state/
```

AgentCrew methodology belongs in `agent-team/`. Do not store project memory inside `agent-team/`.

Global CEO preferences belong in the private profile created by `agentcrew install`. They are not project memory. Never mix `.agent-state/` content between projects or copy product-specific decisions into the global profile.

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
