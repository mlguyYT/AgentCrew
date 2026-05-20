# Skills

Skills are reusable technical and professional capability profiles.

Roles define **what job the agent is doing**.

Skills define **how the agent should perform that job for a specific technology, language, framework, professional practice, or domain**.

Example:

```text
Role: Developer
Skill: Python Pro
Skill: FastAPI
```

This means:

```text
Act as a Developer, and apply Python/FastAPI best practices automatically.
```

---

## How skills are loaded

Agents should read:

```text
agent-team/skills/registry.md
```

Then load matching skill files based on:

- task text
- explicit Skills field
- labels
- changed files
- file extensions
- dependency files
- framework names
- imports and code symbols

---

## Skill file format

Each skill file should include:

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

---

## Adding a new skill

For the canonical authoring process, read:

```text
agent-team/skills/authoring-guide.md
```

1. Create a new file:

```text
agent-team/skills/<category>/<skill-name>.md
```

Recommended categories:

```text
agent-team/skills/languages/
agent-team/skills/frameworks/
agent-team/skills/frontend/
agent-team/skills/platform/
agent-team/skills/professional/
agent-team/skills/ml/
```

2. Add the skill to:

```text
agent-team/skills/registry.md
```

3. Define clear triggers.

Example:

```text
agent-team/skills/frameworks/django.md
```

4. Add registry row:

```md
| Django | `frameworks/django.md` | Django, `manage.py`, `settings.py`, `models.py`, `views.py` |
```

5. Validate the Skill:

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
agent-team/templates/skill-validation-report.md
```

---

## Skill principle

```text
Skills should improve execution quality without changing human approval rules.
```
