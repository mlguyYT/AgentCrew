# Project Presets

## Purpose

Project presets give AgentCrew a fast starting profile for common project shapes.

They help product builders avoid repeating setup guidance like which Skills to load, which validation commands to prefer, and which review gates usually matter.

---

## Run

From a target project:

```bash
~/AgentCrew/bin/agentcrew preset
```

From anywhere:

```bash
~/AgentCrew/bin/agentcrew preset --project /path/to/project
```

This creates or updates:

```text
.agent-state/project-preset.md
```

Use `--dry-run` to preview and `--force` when intentionally replacing an existing preset artifact.

---

## Included Presets

- React frontend
- Python API
- Node service
- general library
- CLI tool

---

## Rules

- Presets are advisory defaults.
- Agents still inspect task-specific files before changing code.
- Repository instructions and human instructions win over preset guidance.
- Presets never bypass testing, review, safety policies, or human approval.

See:

```text
agent-team/playbooks/project-presets.md
agent-team/presets/README.md
agent-team/templates/project-preset.md
agent-team/checklists/project-presets.md
```
