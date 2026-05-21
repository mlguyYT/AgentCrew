# Refactor Recipe

## Use For

Behavior-preserving structural improvement, modularization, cleanup, or architecture simplification.

## Default Route

```text
Developer -> Tester -> Reviewer -> Human
```

## Agent Focus

- define preserved behavior before editing
- extract one boundary at a time
- keep public APIs, data keys, schemas, event names, and external behavior stable unless behavior change is explicit
- add or run tests around existing behavior
- label discovered legacy bugs as follow-up risks instead of silently changing them

## Required Playbook

```text
agent-team/playbooks/behavior-preserving-refactor.md
```
