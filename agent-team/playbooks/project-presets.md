# Project Presets Playbook

## Purpose

Select a compact project-shape preset so AgentCrew can start with sensible defaults for Skills, validation, review gates, and architecture focus.

Presets reduce repeated setup decisions for product builders while keeping task-specific inspection and human approval intact.

---

## When To Use

Use this playbook when:

```yaml
use_when:
  - starting work in a new target project
  - project detection finds a recognizable app shape
  - agents need default validation and review expectations
  - the human asks how AgentCrew should handle this project
```

---

## Selection Rules

```yaml
selection_order:
  - explicit human choice
  - project detector signals
  - package and framework metadata
  - source file patterns
  - generic fallback
```

Load only the selected preset file from `agent-team/presets/`.

---

## Command

```bash
~/AgentCrew/bin/agentcrew preset --project .
```

Use `--dry-run` to preview and `--force` only when replacing `.agent-state/project-preset.md`.

---

## Artifact

Write project-specific preset selections to:

```text
.agent-state/project-preset.md
```

Use:

```text
agent-team/templates/project-preset.md
```

---

## Rules

- Presets are advisory, not authoritative.
- Repository instructions, human instructions, and task-specific evidence win.
- Presets never bypass human approval or safety rules.
- Escalate reviewers and quality gates when risk requires it.
