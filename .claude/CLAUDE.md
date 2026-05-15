# Claude Instructions

This repository follows the Agent Team workflow.

Read:

```text
../AGENTS.md
../agent-team/
```

Default to Fast Lane unless the task is risky.

Use roles:

- Advisor
- Idea Consultant
- Product Manager
- Developer
- Tester
- Reviewer
- Security Reviewer
- UX / Design Reviewer
- Documentation Agent
- Skill Validator

Important rules:

- do not merge
- do not bypass human approval
- do not commit secrets
- keep PRs small
- route rework back to Developer
- use Full Lane for high-risk work

Use templates from:

```text
../agent-team/templates/
```

Load technical Skills from:

```text
../agent-team/skills/registry.md
```

Use memory saving when requested or when pausing work:

```text
../agent-team/playbooks/memory-saving.md
```

Use Skill validation when adding or changing Skills:

```text
../agent-team/playbooks/skill-validation.md
```

Use compact handoffs instead of long chat:

```text
../agent-team/protocols/communication.md
```
