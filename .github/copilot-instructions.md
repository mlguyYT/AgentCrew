# GitHub Copilot Instructions

This repository uses the Agent Team workflow.

Canonical instructions:

```text
AGENTS.md
agent-team/
```

Use Fast Lane by default.

For implementation tasks:

1. read `agent-team/agents/developer.md`
2. read `agent-team/playbooks/pr-process.md`
3. read `agent-team/skills/registry.md`
4. use `agent-team/templates/pr-description.md`

For testing tasks:

1. read `agent-team/agents/tester.md`
2. read `agent-team/skills/registry.md`
3. use `agent-team/templates/test-report.md`

For review tasks:

1. read `agent-team/agents/reviewer.md`
2. read `agent-team/skills/registry.md`
3. use `agent-team/templates/review-report.md`

For specialist review tasks:

- security-sensitive changes: read `agent-team/agents/security-reviewer.md` and use `agent-team/templates/security-review-report.md`
- user-facing UI/UX changes: read `agent-team/agents/ux-design-reviewer.md` and use `agent-team/templates/ux-design-review-report.md`
- docs, examples, changelogs, or release notes: read `agent-team/agents/documentation-agent.md` and use `agent-team/templates/documentation-report.md`

For Skill changes:

1. read `agent-team/agents/skill-validator.md`
2. read `agent-team/playbooks/skill-validation.md`
3. use `agent-team/templates/skill-validation-report.md`

For memory saving:

1. read `agent-team/playbooks/memory-saving.md`
2. use `agent-team/templates/memory-summary.md`

For agent handoffs:

1. read `agent-team/protocols/communication.md`
2. use `agent-team/protocols/handoff-format.md`
3. follow `agent-team/protocols/token-discipline.md`

Never:
- merge PRs automatically
- bypass human approval
- commit secrets
- hide failing tests
- make unrelated changes
