# Skill Validation Playbook

## Purpose

This playbook defines how to validate Skills before they are used by the Agent Team workflow.

Skill validation keeps the Skill registry useful, safe, and predictable.

---

## When to validate

Validate Skills when:

```yaml
validate_when:
  - a new Skill is added
  - an existing Skill is changed
  - Skill categories are reorganized
  - registry triggers are changed
  - a Skill conflicts with another Skill
  - a human requests Skill review
```

---

## Required files

Read:

```text
agent-team/skills/README.md
agent-team/skills/registry.md
agent-team/playbooks/skill-loading.md
agent-team/agents/skill-validator.md
```

Then read the Skill file being validated.

---

## Required Skill sections

Each Skill should include:

```yaml
required_sections:
  - Purpose
  - Applies when
  - Detection triggers
  - Instructions
  - Testing guidance
  - Review checklist
  - Anti-patterns
```

If a section is missing, request rework.

---

## Validation checks

Check:

```yaml
checks:
  path:
    - file is in the right category
    - filename uses kebab-case
    - registry path matches actual file path

  triggers:
    - triggers are specific enough to avoid noisy loading
    - file patterns are realistic
    - code symbols are useful when included

  instructions:
    - guidance is actionable
    - guidance follows repository conventions
    - guidance does not override safety or human approval

  testing:
    - commands are examples, not invented results
    - testing guidance fits the technology
    - failure and limitation reporting is clear

  review:
    - checklist catches meaningful risks
    - anti-patterns are specific
    - conflict behavior is clear
```

---

## Conflict handling

If Skills overlap:

```yaml
resolution:
  - safety rules win
  - human instructions win
  - repository instructions win
  - more specific Skill wins
  - broader Skill supplies general defaults only
```

Example:

```text
FastAPI overrides general Python guidance for API routing details.
Python Pro still applies to Python readability and testing.
```

---

## Output

Use:

```text
agent-team/templates/skill-validation-report.md
```

Possible recommendations:

```yaml
recommendations:
  - valid
  - valid_with_notes
  - rework_required
  - reject
```

---

## Done definition

Skill validation is complete when:

```yaml
done:
  - required sections are checked
  - registry path is checked
  - trigger quality is checked
  - safety conflicts are checked
  - validation recommendation is documented
```
