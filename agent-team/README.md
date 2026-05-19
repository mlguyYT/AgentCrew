# AgentCrew

This folder defines the reusable AgentCrew methodology.

It is designed to be readable by humans and AI coding agents.

AgentCrew should normally be installed once outside target projects and registered with supported coding agents:

```bash
~/AgentCrew/bin/agentcrew install
```

After registration, users should be able to ask for an outcome without saying `Load AgentCrew`.

---

## Roles

```yaml
agents:
  advisor:
    purpose: evaluate idea direction and risk

  idea_consultant:
    purpose: refine raw idea into structured brief

  product_manager:
    purpose: turn ideas into scoped tasks

  developer:
    purpose: implement changes and prepare PRs

  tester:
    purpose: validate behavior and acceptance criteria

  reviewer:
    purpose: review quality, maintainability, and risk

  security_reviewer:
    purpose: review security-sensitive work and data-risk tradeoffs

  ux_design_reviewer:
    purpose: review user-facing changes for usability, accessibility, and visual quality

  documentation_agent:
    purpose: create and review documentation, examples, changelogs, and release notes

  skill_validator:
    purpose: validate Skill quality, triggers, safety, and registry entries
```

---

## Main workflow

Default:

```text
Task
  -> Developer
  -> Tester
  -> Reviewer when risk is meaningful
  -> Product Manager when scope or product behavior changes
  -> Specialist reviewer if needed
  -> Human approval
```

For larger work:

```text
Idea
  -> Advisor
  -> Idea Consultant
  -> Product Manager
  -> Developer
  -> Tester
  -> Reviewer
  -> Specialist reviewer if needed
  -> Human approval
```

Specialist reviewers are Security Reviewer, UX / Design Reviewer, and Documentation Agent. Use them only when the task touches their area.

---

## How agents should use this folder

If the user does not name a role, lane, or Skill, infer them from the request.
Use `agent-team/playbooks/task-classification.md` to choose the lane and starting role, then use `agent-team/playbooks/skill-loading.md` to load matching Skills.

Before acting, an agent should:

1. read `AGENTS.md`
2. read the relevant role file in `agent-team/agents/`
3. read the relevant playbook in `agent-team/playbooks/`
4. use `agent-team/playbooks/specialist-review-routing.md` when specialist review may apply
5. use `agent-team/playbooks/default-branch-merge.md` before default-branch merge readiness
6. use `agent-team/playbooks/dependency-supply-chain.md` for dependency, runtime, container, CI, or build-system changes
7. use `agent-team/playbooks/behavior-preserving-refactor.md` for refactors
8. use `agent-team/playbooks/compatibility-rollout.md` for protocol, API, auth, config, or client/server compatibility changes
9. use `agent-team/playbooks/lane-escalation.md` if risk changes
10. read `agent-team/skills/registry.md` and load matching Skills
11. use `agent-team/protocols/communication.md` for handoffs
12. use the relevant output template in `agent-team/templates/`

When saving handoff context, use:

```text
agent-team/playbooks/memory-saving.md
agent-team/templates/memory-summary.md
```

The optional local checkpoint utility is:

```text
~/AgentCrew/agent-team/tools/save-session.sh
~/AgentCrew/agent-team/tools/list-sessions.sh
```

When adding or changing Skills, use:

```text
agent-team/skills/authoring-guide.md
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
agent-team/templates/skill-validation-report.md
```

For agent-to-agent handoffs, use:

```text
agent-team/protocols/communication.md
agent-team/protocols/handoff-format.md
agent-team/protocols/state-artifacts.md
agent-team/protocols/token-discipline.md
```

After placing AgentCrew outside a project, run:

```text
~/AgentCrew/agent-team/checklists/agentcrew-health-check.md
```

For tool-specific loading behavior, use:

```text
agent-team/adapters/
docs/auto-load.md
```

---

## Default behavior

```yaml
default:
  lane: Fast Lane
  planning_depth: minimal
  review_depth: risk_based
  skill_loading: automatic
  skill_validation: required_for_skill_changes
  memory_saving: on_pause_or_request
  handoffs: compact_artifacts
  state_artifacts: .agent-state/
  approval: human
```

---

## Quality goal

The system aims to be:

```text
fast enough for startups
structured enough for quality
simple enough to actually use
```
