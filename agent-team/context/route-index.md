# Route Index

## Purpose

Use this file immediately after `AGENTS.md` to route work without loading the whole AgentCrew methodology.

## Always Remember

- Human approval remains final.
- Agents must not merge, approve as human, bypass protection, hide failures, commit secrets, or make unrelated changes.
- Default lane is Fast Lane.
- Default quality profile is standard unless project or task context says otherwise.
- If `.agent-state/project-constraints.md` exists, load it before code, docs, cloud, public artifact, commit/push, review, or memory work.
- Load detailed files only after routing confirms they apply.
- For advisory questions, load no additional AgentCrew files unless evidence or implementation is needed.

## Route First

For obvious requests, use this table directly. For ambiguous requests or multi-intent work, load `agent-team/playbooks/request-routing.md`.

```yaml
direct_question_or_advice: Direct Answer Mode -> Human
small_scoped_task: Developer -> Tester -> Human
small_task_with_meaningful_risk: Developer -> Tester -> Reviewer -> Human
scope_or_product_behavior_change: Product Manager -> Developer -> Tester -> Human
portfolio_or_target_role_project: Product Manager -> Researcher Agent if job evidence is needed -> Human scope approval
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
- `agent-team/playbooks/project-presets.md` when project-shape defaults help
- `agent-team/playbooks/project-constraints.md` for standing constraints, no-commit mode, or public/private/cloud constraints
- `agent-team/playbooks/cloud-operations.md` for cost-bearing or deployed resources
- `agent-team/playbooks/artifact-classification.md` for generated, ignored, cloud, or temporary artifacts
- `agent-team/playbooks/public-private-boundary.md` for private product, customer, commercial, or strategy boundaries
- `agent-team/playbooks/portfolio-project-scope.md` for portfolio, resume, interview, case-study, or target-role projects
- `agent-team/playbooks/task-intake.md` for `.agent-state/current-task.md`
- `agent-team/playbooks/acceptance-criteria.md` for `.agent-state/task-brief.md`
- `agent-team/playbooks/work-planning.md` for `.agent-state/work-plan.md`
- `agent-team/playbooks/implementation-readiness.md` before Developer starts non-trivial work
- `agent-team/playbooks/pr-preparation.md` before human PR review
- `agent-team/playbooks/release-management.md` for release, rollout, rollback, or deployment preparation
- `agent-team/playbooks/support-triage.md` for support, customer reports, severity, impact, or reproduction
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
