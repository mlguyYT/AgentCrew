# Route Index

## Purpose

Use this file immediately after `AGENTS.md` to route work without loading the whole AgentCrew methodology.

## Always Remember

- Human approval remains final.
- Agents must not merge, approve as human, bypass protection, hide failures, commit secrets, or make unrelated changes.
- Default lane is Fast Lane.
- Default quality profile is standard unless project or task context says otherwise.
- Load detailed files only after routing confirms they apply.
- For advisory questions, load no additional AgentCrew files unless evidence or implementation is needed.

## Route First

For obvious requests, use this table directly. For ambiguous requests or multi-intent work, load `agent-team/playbooks/request-routing.md`.

```yaml
direct_question_or_advice: Direct Answer Mode -> Human
small_scoped_task: Developer -> Tester -> Human
small_task_with_meaningful_risk: Developer -> Tester -> Reviewer -> Human
scope_or_product_behavior_change: Product Manager -> Developer -> Tester -> Human
high_risk_or_ambiguous: Full Lane
review_request: Reviewer
validation_request: Tester
research_question: Researcher Agent
llm_or_rag_work: LLM Agent when triggered
computer_vision_or_cnn_work: CNN Agent when triggered
docs_change: Documentation Agent when useful
support_or_customer_report: Support Triage Agent
release_request: Release Manager
skill_change: Skill Validator
```

## Load Next

Load only:

- no additional files for Direct Answer Mode
- selected context profile from `agent-team/context/`
- selected role file from `agent-team/agents/`
- `agent-team/playbooks/request-routing.md` only when route is ambiguous
- `agent-team/playbooks/project-presets.md` when project-shape defaults would help
- `agent-team/playbooks/task-intake.md` when creating `.agent-state/current-task.md`
- `agent-team/playbooks/acceptance-criteria.md` when creating `.agent-state/task-brief.md`
- `agent-team/playbooks/work-planning.md` when creating `.agent-state/work-plan.md`
- `agent-team/playbooks/implementation-readiness.md` before Developer starts non-trivial work
- `agent-team/playbooks/pr-preparation.md` before human PR review when a compact approval packet is useful
- `agent-team/playbooks/release-management.md` when release readiness, rollout, rollback, or deployment preparation is in scope
- `agent-team/playbooks/support-triage.md` when support tickets, customer reports, severity, impact, or reproduction triage is in scope
- selected `agent-team/recipes/*.md` when a recipe changes handling
- selected lane playbook
- `agent-team/playbooks/quality-profile-selection.md` when profile choice affects gates or output detail
- selected `agent-team/quality-profiles/*.md` only when needed
- `agent-team/skills/registry.md`
- matching skill files only
- triggered gate playbooks only
- output template for the current phase
- `agent-team/templates/task-routing.md` when a compact route summary is useful

Do not load `README.md`, `docs/`, `examples/`, or `STRUCTURE.md` during normal target-project work unless editing AgentCrew or debugging installation.
