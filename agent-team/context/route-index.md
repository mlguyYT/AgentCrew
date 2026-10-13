# Route Index

## Purpose

Use this file immediately after `AGENTS.md` to route work without loading the whole AgentCrew methodology.

## Always Remember

- Human approval remains final.
- Never merge, approve as human, bypass protection, hide failures, commit secrets, or make unrelated changes.
- Default lane is Fast Lane.
- Default quality profile is standard unless project or task context says otherwise.
- Load `.agent-state/project-constraints.md` before affected work.
- Load details only after routing confirms they apply.
- For advisory questions, load no additional AgentCrew files unless evidence or implementation is needed.
- For product work, treat the user as CEO and handle internal role selection and coordination automatically.

## Route First

For obvious requests, use this table directly. For ambiguous requests or multi-intent work, load `agent-team/playbooks/request-routing.md`.

```yaml
direct_question_or_advice: Direct Answer Mode -> Human
product_idea_or_direction: Advisor -> Idea Consultant -> Product Manager -> Human
product_idea_plus_delivery: Advisor -> Idea Consultant -> Product Manager -> Human decision -> delivery team -> Human
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
architecture_or_system_design: Software Architect Agent when triggered
docs_change: Documentation Agent when useful
support_or_customer_report: Support Triage Agent
release_request: Release Manager
skill_change: Skill Validator
```

## Load Next

Load only:

- no additional files for Direct Answer Mode
- `agent-team/context/ceo-operating-context.md` for non-trivial product or repository work
- `agent-team/playbooks/idea-to-product.md` for product ideas and idea-led delivery
- selected context profile from `agent-team/context/`
- selected role file from `agent-team/agents/`
- `agent-team/playbooks/request-routing.md` only when route is ambiguous
- `agent-team/playbooks/project-presets.md` when project-shape defaults help
- boundary playbooks for project constraints, cloud operations, artifact classification, or public/private decisions
- `agent-team/playbooks/portfolio-project-scope.md` for portfolio, resume, interview, case-study, or target-role projects
- `agent-team/playbooks/architecture-decisions.md` for significant boundaries, contracts, data ownership, runtime dependencies, or quality attributes
- task lifecycle playbooks for intake, acceptance criteria, planning, readiness, and PR preparation
- `agent-team/playbooks/release-management.md` for release, rollout, rollback, or deployment preparation
- `agent-team/playbooks/support-triage.md` for support, customer reports, severity, impact, or reproduction
- selected recipe when it changes handling
- selected lane playbook
- quality-profile guidance only when profile choice affects handling
- selected `agent-team/quality-profiles/*.md` only when needed
- `agent-team/skills/registry.md`
- matching Skills, triggered gates, and the current output template
- `agent-team/templates/task-routing.md` when a compact route summary is useful

Do not load `README.md`, `docs/`, `examples/`, or `STRUCTURE.md` during normal target-project work unless editing AgentCrew or debugging installation.
