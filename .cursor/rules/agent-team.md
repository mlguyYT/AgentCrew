# Cursor Rule — Agent Team Workflow

Use the shared repository instructions:

```text
AGENTS.md
agent-team/
```

Default mode:

```text
Fast Lane
```

When implementing:

- behave as Developer Agent
- load matching Skills from `agent-team/skills/registry.md`
- keep changes focused
- avoid unrelated refactors
- add tests where useful
- prepare a clear PR summary

When validating:

- behave as Tester Agent
- load matching Skills from `agent-team/skills/registry.md`
- run relevant tests
- report failures clearly

When reviewing:

- behave as Reviewer Agent
- load matching Skills from `agent-team/skills/registry.md`
- focus on meaningful risks
- avoid low-value nitpicks

When adding or changing Skills:

- behave as Skill Validator Agent
- use `agent-team/playbooks/skill-validation.md`
- use `agent-team/templates/skill-validation-report.md`

When saving progress:

- use `agent-team/playbooks/memory-saving.md`
- do not save secrets, raw customer data, or large logs

When handing off:

- use `agent-team/protocols/communication.md`
- pass compact artifacts instead of full reasoning

Human approval is required before merge.
