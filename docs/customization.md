# Customization Guide

## Purpose

This guide explains how to adapt the Agent Team workflow to your project.

---

## Customize roles

You may add specialized versions of existing roles.

Examples:

```yaml
developer_specializations:
  - frontend
  - backend
  - mobile
  - infra
  - data

tester_specializations:
  - regression
  - e2e
  - api
  - performance

reviewer_specializations:
  - code
  - architecture
  - security
  - infra
```

---

## Add a new agent

To add a new role:

1. create a file in `agent-team/agents/`
2. define purpose
3. define responsibilities
4. define when to use it
5. define output format
6. update `AGENTS.md`
7. update relevant playbooks

Example:

```text
agent-team/agents/security-reviewer.md
```

---

## Add a new Skill

To add a new technical Skill:

1. create the Skill in the most specific category
2. add it to `agent-team/skills/registry.md`
3. define triggers, instructions, testing guidance, review checklist, and anti-patterns

Recommended categories:

```text
agent-team/skills/languages/
agent-team/skills/frameworks/
agent-team/skills/frontend/
agent-team/skills/platform/
agent-team/skills/professional/
```

Example:

```text
agent-team/skills/frameworks/django.md
```

---

## Customize lanes

You can rename lanes.

Default:

```yaml
lanes:
  - Fast Lane
  - Full Lane
```

Alternative:

```yaml
lanes:
  - Lightweight
  - Structured
```

Keep the meaning clear.

---

## Customize PR rules

Edit:

```text
agent-team/playbooks/pr-process.md
```

Common customizations:

```yaml
custom_pr_rules:
  - require reviewer for all PRs
  - require tests for all code changes
  - require screenshots for UI changes
  - require migration notes for database changes
```

---

## Customize task templates

Edit:

```text
agent-team/templates/task.md
```

Add fields your team needs:

```yaml
possible_fields:
  - estimate
  - owner
  - customer impact
  - rollback plan
  - feature flag
  - observability
```

---

## Customize for larger teams

For larger teams, add:

```yaml
larger_team_additions:
  - tech lead reviewer
  - security reviewer
  - release manager
  - documentation agent
  - support agent
```

But keep the default workflow simple.

---

## Recommended rule

Do not add roles until you feel pain.

```text
Start simple.
Add structure only when useful.
```
