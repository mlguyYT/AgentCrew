# Codex Instructions

Use the repository-level agent team instructions.

Canonical files:

```text
../AGENTS.md
../agent-team/
```

Before doing work:

1. read `../AGENTS.md`
2. read the relevant file in `../agent-team/agents/`
3. read the relevant playbook in `../agent-team/playbooks/`
4. read `../agent-team/skills/registry.md` and load matching Skills
5. use the relevant template in `../agent-team/templates/`

Default workflow:

```text
Fast Lane
```

Rules:

- keep PRs small
- do not merge
- do not bypass human approval
- do not commit secrets
- route rework back to Developer
- use Full Lane for risky work

When asked to act as a role, use the matching file:

```text
Advisor -> ../agent-team/agents/advisor.md
Idea Consultant -> ../agent-team/agents/idea-consultant.md
Product Manager -> ../agent-team/agents/product-manager.md
Developer -> ../agent-team/agents/developer.md
Tester -> ../agent-team/agents/tester.md
Reviewer -> ../agent-team/agents/reviewer.md
Security Reviewer -> ../agent-team/agents/security-reviewer.md
UX / Design Reviewer -> ../agent-team/agents/ux-design-reviewer.md
Documentation Agent -> ../agent-team/agents/documentation-agent.md
Skill Validator -> ../agent-team/agents/skill-validator.md
```

When saving progress, use:

```text
../agent-team/playbooks/memory-saving.md
../agent-team/templates/memory-summary.md
```

When adding or changing Skills, use:

```text
../agent-team/playbooks/skill-validation.md
../agent-team/templates/skill-validation-report.md
```

For agent handoffs, use compact artifacts:

```text
../agent-team/protocols/communication.md
../agent-team/protocols/handoff-format.md
../agent-team/protocols/token-discipline.md
```
