# Skill Loading Playbook

## Purpose

This playbook explains how agents should automatically select and apply technical skills.

Roles decide the agent's responsibility.

Skills decide the technical execution style.

---

## Core idea

```text
Role + Skills = Behavior
```

Example:

```text
Developer + Python Pro + FastAPI
```

Means:

```text
Implement the task as Developer, using Python and FastAPI best practices.
```

---

## Skill loading process

Before acting:

1. Read `AGENTS.md`
2. Read `agent-team/context/route-index.md`
3. Read the selected context profile
4. Read the relevant role file
5. Read compact `agent-team/skills/registry.md`
6. Inspect task and repository context
7. Select matching skills
8. Read selected skill files using the paths in the registry
9. Load `agent-team/skills/registry-guidance.md` only if matching is ambiguous
10. Apply role + skills together

---

## Detection inputs

Use:

```yaml
inputs:
  - explicit Skills field
  - task title
  - task description
  - acceptance criteria
  - labels
  - changed files
  - file extensions
  - dependency files
  - imports
  - framework names
```

---

## Explicit skills

If the task says:

```md
## Skills
- python-pro
- fastapi
```

Load those skills.

Explicit Skills are optional. If the user only asks for an outcome, infer Skills from the task and repository context.

---

## Automatic skills

If task says:

```text
Fix validation in FastAPI endpoint
```

Load:

```text
python-pro
fastapi
```

If changed files include:

```text
src/components/Button.tsx
```

Load:

```text
react
```

If changed files include:

```text
infra/k8s/deployment.yaml
```

Load:

```text
kubernetes
```

---

## Multiple skills

Multiple skills may apply, but load only skills that directly affect the current task. Use `agent-team/skills/registry-guidance.md` only when priority or matching examples are needed.

Example:

```text
Update a FastAPI endpoint and its Kubernetes deployment.
```

Load:

```yaml
skills:
  - python-pro
  - fastapi
  - kubernetes
```

Apply each skill only to the relevant part of the task.

By default, avoid loading more than three skill files unless the task clearly spans more domains or the human asks for full coverage.

---

## Conflict handling

If skills conflict:

```yaml
resolution:
  - safety rules win
  - human instructions win
  - more specific skill wins
  - repository conventions win over generic style
```

---

## Output behavior

For bigger tasks, mention Skills applied when useful:

```md
## Skills Applied
- python-pro
- fastapi
```

For small tasks, this is optional.

Do not let `## Skills Applied` become ceremony. Use it when it clarifies which technical guidance affected the work.
Do not paste skill contents into the response; cite the skill names only when useful.

---

## Adding new skills

To add a skill:

1. create:

```text
agent-team/skills/<category>/<skill-name>.md
```

2. update:

```text
agent-team/skills/registry.md
```

3. include triggers and instructions.

---

## Done definition

Skill loading is successful when:

- relevant skills are identified
- matching skill files are read
- task is executed according to role and skills
- no safety rule is overridden
