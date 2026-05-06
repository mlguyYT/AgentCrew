# Workflow: Task → Pull Request

## Purpose
Turn a task into a working PR.

---

## Flow

```text
Task
  -> Developer
  -> Pull Request
```

---

## Step 1 — Task input

Task must include:
- description
- acceptance criteria
- scope

Use:
agent-team/templates/task.md

---

## Step 2 — Developer implementation

Developer:
- inspects repo
- writes code
- adds tests
- keeps scope small

---

## Step 3 — PR creation

PR must follow:
agent-team/templates/pr-description.md

---

## Output

```yaml
output:
  - PR branch
  - PR description
  - code changes
```
