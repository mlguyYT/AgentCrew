# Skill Authoring Guide

## Purpose

Use this guide when adding or changing AgentCrew Skills.

Skills define technical or professional execution guidance. They help a role do better work in a specific language, framework, platform, or practice area.

Skills never override safety rules, repository instructions, or human approval.

---

## Create A Skill

Add a file under the most specific category:

```text
agent-team/skills/languages/
agent-team/skills/frameworks/
agent-team/skills/frontend/
agent-team/skills/platform/
agent-team/skills/professional/
```

Use kebab-case:

```text
agent-team/skills/frameworks/django.md
agent-team/skills/frontend/vue.md
agent-team/skills/platform/terraform.md
```

---

## Required Sections

Each Skill should include:

```text
# Skill Name

## Purpose

## Applies when

## Detection triggers

## Instructions

## Testing guidance

## Review checklist

## Anti-patterns
```

Keep guidance actionable. Avoid generic advice that could apply to every project.

---

## Trigger Format

Use concrete triggers:

```yaml
triggers:
  task_text:
    - Django
    - ORM model
  files:
    - manage.py
    - "**/settings.py"
    - "**/models.py"
  dependencies:
    - django
  commands:
    - python manage.py test
```

Triggers should be specific enough that agents do not load the Skill for unrelated work.

---

## Registry Entry

Add the Skill to:

```text
agent-team/skills/registry.md
```

Example:

```md
| Django | `frameworks/django.md` | Django, `manage.py`, `settings.py`, `models.py`, migrations |
```

---

## Conflict Rules

When Skills overlap:

```yaml
resolution:
  - safety rules win
  - human instructions win
  - repository-specific instructions win
  - more specific Skill wins
  - broader Skill supplies general defaults only
```

Example:

```text
Django overrides Python Pro for Django routing, settings, models, and migrations.
Python Pro still applies to Python readability, typing, and tests.
```

---

## Good Skill Guidance

Good:

```text
For migrations, include rollback notes and a test or manual validation path.
```

Weak:

```text
Write clean code.
```

Good:

```text
For React forms, cover loading, empty, error, and disabled states.
```

Weak:

```text
Make the UI good.
```

---

## Validation

After adding or changing a Skill:

1. Read `agent-team/agents/skill-validator.md`.
2. Follow `agent-team/playbooks/skill-validation.md`.
3. Use `agent-team/templates/skill-validation-report.md`.

The Skill Validator checks:

- file path and naming
- registry accuracy
- trigger quality
- safety conflicts
- testing guidance
- review checklist usefulness
- overlap with existing Skills

---

## Done Definition

A Skill is ready when:

- required sections exist
- registry entry points to the right file
- triggers are specific and useful
- guidance is actionable
- testing guidance is practical
- anti-patterns catch real failure modes
- no instruction bypasses human approval or safety rules
