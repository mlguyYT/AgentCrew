# Naming Convention

## Purpose

AgentCrew files should be predictable because agents follow paths literally.

Use this convention for all reusable workflow files in `agent-team/`.

---

## File Names

Use kebab-case:

```text
idea-consultant.md
product-manager.md
security-reviewer.md
ux-design-reviewer.md
documentation-agent.md
skill-validator.md
task-classification.md
specialist-review-routing.md
lane-escalation.md
state-artifacts.md
```

Avoid mixed styles:

```text
product_manager.md
ProductManager.md
productManager.md
product manager.md
```

---

## Role Names

Use readable title case in prose:

```text
Idea Consultant
Product Manager
Security Reviewer
UX / Design Reviewer
Documentation Agent
LLM Agent
Researcher Agent
CNN Agent
Skill Validator
```

Use kebab-case for role files:

```text
agent-team/agents/idea-consultant.md
agent-team/agents/product-manager.md
agent-team/agents/security-reviewer.md
agent-team/agents/ux-design-reviewer.md
agent-team/agents/documentation-agent.md
agent-team/agents/llm-agent.md
agent-team/agents/researcher-agent.md
agent-team/agents/cnn-agent.md
agent-team/agents/skill-validator.md
```

---

## Role Naming Rule

Use `Agent` for roles. Avoid `Expert` in role names because it can imply authority beyond the workflow. Agents recommend, validate, and prepare work. Humans remain final decision-makers.

---

## Skill Names

Use readable names in the registry table:

```text
Python Pro
FastAPI
Reviewer Pro
Product Owner Pro
```

Use kebab-case for skill files:

```text
python-pro.md
fastapi.md
reviewer-pro.md
product-owner-pro.md
```

---

## Artifact Names

Use stable names in `.agent-state/`:

```text
current-task.md
decisions.md
handoff.md
test-report.md
review-report.md
memory.md
```

Do not store project-specific working state inside `agent-team/`.

---

## Rule

When adding a new role, playbook, Skill, protocol, template, checklist, or policy:

1. Choose a kebab-case file name.
2. Use clear title case in the heading.
3. Add the file to `agent-team/STRUCTURE.md` if it is part of the reusable package.
4. Add registry or routing entries when agents need to discover it.
