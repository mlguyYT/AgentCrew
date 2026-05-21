# Request Routing Playbook

## Purpose

Route normal user requests without requiring the user to name AgentCrew, a lane, a role, or a Skill.

Users should be able to ask for the outcome directly. AgentCrew is responsible for choosing the starting role, lane, Skills, quality gates, and next human approval point.

---

## Routing Order

Use this order before loading detailed role files or Skills. For a quick machine-readable preview, use `agentcrew classify`:

```bash
~/AgentCrew/bin/agentcrew classify "Add OAuth login"
```

Then apply this order:

```yaml
routing_order:
  - understand the requested outcome
  - identify whether the user asked for planning, implementation, validation, review, research, or documentation
  - classify risk using route-index and task-classification
  - choose Fast Lane or Full Lane
  - select the quality profile
  - select the workflow recipe
  - choose the starting role
  - run project detection when stack context is unclear and the detector is available
  - select candidate Skills from the registry
  - identify required gates and specialist triggers
  - produce a compact route summary
  - create `.agent-state/current-task.md` when a durable current task artifact is useful
  - start the workflow
```

Do not ask the user to choose the lane, role, or Skill unless the request is genuinely blocked by missing product direction, access, or risk acceptance.

---

## Intent Mapping

```yaml
intent_to_starting_role:
  rough_idea_or_strategy: Advisor
  product_scope_or_acceptance_criteria: Product Manager
  implementation_or_bug_fix: Developer
  validation_or_regression_check: Tester
  code_or_pr_review: Reviewer
  docs_examples_or_changelog: Documentation Agent
  source_backed_research_or_current_info: Researcher Agent
  prompt_rag_tool_calling_or_model_behavior: LLM Agent
  computer_vision_cnn_training_or_inference: CNN Agent
  skill_creation_or_skill_change: Skill Validator
```

When a request contains multiple intents, start with the earliest role that can clarify scope safely.

Examples:

```text
"Improve onboarding" -> Product Manager first, then Developer/Tester/UX if scope is clear
"Fix onboarding button alignment" -> Developer first, then Tester/UX if user-facing risk remains
"Review this auth PR" -> Reviewer plus Security Reviewer
"Research payment provider options" -> Researcher Agent, then Product Manager
```

---

## Lane Selection

Default to Fast Lane for small, reversible work.

```yaml
fast_lane_when:
  - scoped bug fix
  - isolated UI or copy change
  - docs update
  - small test addition
  - small internal refactor with preserved behavior
  - clear implementation task with low blast radius
```

Use Full Lane when risk, ambiguity, or product impact is meaningful.

```yaml
full_lane_when:
  - authentication or authorization
  - billing or payments
  - customer data or sensitive data
  - database migration or data loss risk
  - infrastructure, deployment, CI, runtime, or container change
  - public API, protocol, compatibility, or rollout change
  - large refactor or architecture decision
  - unclear product direction
  - rollback is difficult
```

If risk increases during work, load `agent-team/playbooks/lane-escalation.md` and escalate.

## Quality Profile Selection

Default to `standard` for maintained products and normal production repositories. Use `agent-team/playbooks/quality-profile-selection.md` when the product context, risk level, or output depth is unclear.

```yaml
quality_profile_defaults:
  light: solo builders, prototypes, docs-only updates, tiny reversible fixes
  standard: maintained products, startup teams, normal production repositories
  strict: enterprise teams, critical flows, shared platforms, complex refactors
  regulated: compliance, privacy, safety, financial, contractual, or audit-heavy work
```

Load only the selected profile file from `agent-team/quality-profiles/` when it changes gates, evidence, or output detail.

## Workflow Recipe Selection

Use `agent-team/recipes/` to attach a lightweight handling pattern to common outcomes.

```yaml
recipe_defaults:
  bug-fix: focused defect correction
  feature: new or changed product capability
  refactor: behavior-preserving structural improvement
  docs-update: documentation, examples, changelog, release notes
  review: code, PR, architecture, or quality review
  validation: testing, QA, regression, acceptance validation
  research: source-backed investigation or option comparison
  release: release readiness, changelog, version, PR preparation
  incident: production issue, urgent regression, rollback decision
  skill-change: AgentCrew Skill creation or update
```

Load only the selected recipe file when it changes role order, gates, or evidence expectations.

---

## Conditional Fast Lane Steps

Fast Lane is not always only Developer -> Tester. Add steps when triggered:

```yaml
reviewer_required_when:
  - public API or protocol changes
  - security, auth, authorization, dependency, runtime, production config, or default-branch merge risk
  - behavior-changing refactor
  - shared module or large diff
  - tester uncertainty

product_manager_required_when:
  - user-visible behavior changes
  - compatibility or rollout decision
  - unclear acceptance criteria
  - migration tradeoff
  - scope changes during implementation

specialist_required_when:
  - specialist-review-routing trigger is present
```

Fast Lane examples:

```text
Developer -> Tester -> Human
Developer -> Tester -> Reviewer -> Human
Product Manager -> Developer -> Tester -> Reviewer -> Human
Developer -> Tester -> Security Reviewer -> Human
```

---

## Skill Selection

Load `agent-team/skills/registry.md` after the route is known.

Select Skills from:

```yaml
skill_signals:
  - explicit user request
  - detected project profile
  - file extensions
  - dependency files
  - imports and framework names
  - changed files
  - task domain
```

Load only matching Skill files. Do not load all Skills for a small task.

---

## Compact Route Summary

For non-trivial work, report the route in a compact form before executing. Use `agent-team/templates/task-routing.md`.

Keep the route summary short:

```text
Route: Fast Lane
Profile: standard
Recipe: bug-fix
Start: Developer
Skills: typescript-pro, react
Gates: Tester, UX if UI behavior changes
Human approval: final behavior and merge
```

For tiny work, the route summary can be one sentence.

---

## Manual Overrides

If the user explicitly names a role, lane, or Skill, honor it unless it conflicts with safety rules, repository instructions, or human-only decisions.

Examples:

```text
"Act as Reviewer" -> start as Reviewer
"Use Full Lane" -> use Full Lane
"Skip tests" -> do not skip silently; explain the quality gate and ask for human decision if needed
"Merge it" -> do not merge unless the human has explicitly authorized that action and repository rules allow it
```

---

## Ask The Human Only When Needed

Ask before proceeding only when:

```yaml
ask_when:
  - product direction is unclear and multiple outcomes would be materially different
  - risk acceptance is required
  - data loss, security, migration, public behavior, or legacy compatibility decision is needed
  - required credentials or environment access is missing
  - the requested action conflicts with safety or repository rules
```

Otherwise, classify, route, and proceed.
