# Contributing

## Welcome

Contributions are welcome.

Useful contributions include:

- new agent role definitions
- better playbooks
- better templates
- new or improved Skills
- examples
- tool adapter files
- documentation improvements

---

## Contribution principles

Please keep contributions:

```yaml
principles:
  - tool-agnostic
  - startup-friendly
  - human-in-the-loop
  - simple by default
  - easy to copy into projects
```

---

## Before submitting

Check:

```yaml
checklist:
  - does this preserve human approval?
  - does this avoid autonomous merge?
  - is this understandable by humans and agents?
  - is the workflow still lightweight?
  - are examples included if needed?
```

---

## File style

Use:

- Markdown
- clear headings
- short sections
- examples
- YAML blocks for rules
- text diagrams for flows

---

## Adding a new agent

Add:

```text
agent-team/agents/new-agent.md
```

Include:

```yaml
required_sections:
  - Purpose
  - When to use
  - Do not use for
  - Responsibilities
  - Input
  - Output
  - Rules
  - Operating principle
```

---

## Adding a playbook

Add:

```text
agent-team/playbooks/new-playbook.md
```

Include:

```yaml
required_sections:
  - Purpose
  - Flow
  - Rules
  - Examples
  - Done definition
```

---

## Adding a Skill

Add Skills under:

```text
agent-team/skills/languages/
agent-team/skills/frameworks/
agent-team/skills/frontend/
agent-team/skills/platform/
agent-team/skills/professional/
```

Then update:

```text
agent-team/skills/registry.md
```

Validate the Skill with:

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
agent-team/templates/skill-validation-report.md
```

---

## Memory guidance changes

Memory workflow changes belong in:

```text
agent-team/playbooks/memory-saving.md
agent-team/checklists/memory-saving.md
agent-team/templates/memory-summary.md
```

Project-specific memory should be saved outside `agent-team/`.
