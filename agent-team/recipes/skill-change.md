# Skill Change Recipe

## Use For

Adding, editing, validating, or registering AgentCrew Skills.

## Default Route

```text
Skill Validator -> Human
```

## Agent Focus

- keep triggers specific
- avoid unsafe or overbroad instructions
- ensure the registry path matches the skill file
- include examples and conflict rules when useful
- validate that Skills do not override human approval or repository safety rules

## Required Playbook

```text
agent-team/playbooks/skill-validation.md
```
