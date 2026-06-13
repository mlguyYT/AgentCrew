# Workflow Recipes

## Purpose

Workflow recipes are small routing presets for common product-builder requests.

They let users ask for outcomes naturally while AgentCrew picks a practical handling pattern such as bug fix, feature, refactor, docs update, review, validation, research, portfolio project, release, incident, or Skill change.

---

## How Recipes Are Used

`agentcrew classify` prints a selected recipe:

```bash
~/AgentCrew/bin/agentcrew classify "Fix the login validation bug"
```

Example output:

```yaml
recipe: 'bug-fix'
```

`agentcrew start` also writes the recipe to `.agent-state/current-task.md` so later agents can resume with the same handling pattern.

---

## Available Recipes

```text
agent-team/recipes/bug-fix.md
agent-team/recipes/feature.md
agent-team/recipes/refactor.md
agent-team/recipes/docs-update.md
agent-team/recipes/review.md
agent-team/recipes/validation.md
agent-team/recipes/research.md
agent-team/recipes/portfolio-project.md
agent-team/recipes/release.md
agent-team/recipes/incident.md
agent-team/recipes/skill-change.md
```

---

## Rules

- Recipes tune workflow defaults; they do not override safety rules.
- Load only the selected recipe file.
- Escalate lane, quality profile, reviewer, and specialist gates when risk requires it.
- Human approval remains final.
