# Skill Validation

## Purpose

Skill validation checks that a Skill is useful, detectable, safe, and consistent before it is added to the registry.

## Core files

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
agent-team/checklists/skill-validation.md
agent-team/templates/skill-validation-report.md
```

## Recommended use

Ask the agent:

```text
Act as Skill Validator Agent.
Validate this Skill using agent-team/playbooks/skill-validation.md.
Use agent-team/templates/skill-validation-report.md.
```

## What is checked

- required sections
- registry path
- trigger quality
- safety rules
- testing guidance
- review checklist
- overlap with existing Skills

## Possible recommendations

```yaml
recommendations:
  - valid
  - valid_with_notes
  - rework_required
  - reject
```
