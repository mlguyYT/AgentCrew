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

Read:

```text
agent-team/skills/authoring-guide.md
```

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

## Adding an Agent

When adding a new agent role:

1. add `agent-team/agents/<role>.md`
2. add any needed template under `agent-team/templates/`
3. add any needed checklist under `agent-team/checklists/`
4. update `AGENTS.md`, `agent-team/README.md`, and `agent-team/STRUCTURE.md`
5. update usage docs and adapters
6. keep human approval and no-merge rules intact

---

## Memory guidance changes

Memory workflow changes belong in:

```text
agent-team/playbooks/memory-saving.md
agent-team/checklists/memory-saving.md
agent-team/templates/memory-summary.md
```

Project-specific memory should be saved outside `agent-team/`.

Current task state belongs in `.agent-state/` and should follow:

```text
agent-team/protocols/state-artifacts.md
```
