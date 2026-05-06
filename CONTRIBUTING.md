# Contributing

Contributions are welcome.

For the detailed contribution guide, see:

```text
docs/contributing.md
```

Useful contributions include:

- clearer role definitions
- better playbooks
- stronger templates
- new Skills
- examples
- tool adapter files
- documentation improvements

## Principles

Keep contributions:

- tool-agnostic
- human-in-the-loop
- simple by default
- easy to copy into another project
- clear enough for both humans and agents

## Core versus runtime

Put reusable workflow content in `agent-team/`.

Put optional orchestration, container, Kubernetes, GitHub App, or local runtime content in `runtime/`.

## Adding a role

Add the role file under:

```text
agent-team/agents/
```

Use kebab-case filenames. Keep role IDs in snake_case when needed.

## Adding a Skill

Add the Skill under the most specific category:

```text
agent-team/skills/languages/
agent-team/skills/frameworks/
agent-team/skills/frontend/
agent-team/skills/platform/
```

Then update:

```text
agent-team/skills/registry.md
```

Then validate it with:

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
```

## Memory-related changes

Memory guidance belongs in:

```text
agent-team/playbooks/memory-saving.md
agent-team/checklists/memory-saving.md
agent-team/templates/memory-summary.md
```

Do not add project-specific memory entries to `agent-team/`.

## Before submitting

Check:

- human approval rules are preserved
- agents still cannot merge PRs
- scope control is not weakened
- Skill changes have validation guidance
- examples and paths still match the folder structure
- docs do not imply the optional runtime is required
