# Project Presets

## Purpose

Project presets are compact guidance profiles for common project shapes.

They help AgentCrew choose default Skills, validation commands, review gates, architecture focus, and documentation expectations without loading every Skill or playbook.

---

## Available Presets

```yaml
presets:
  react_frontend: react-frontend.md
  python_api: python-api.md
  python_web: python-web.md
  node_service: node-service.md
  rust_cli: rust-cli.md
  mobile: mobile.md
  ml_pipeline: ml-pipeline.md
  general_library: general-library.md
  cli_tool: cli-tool.md
```

---

## Rules

- Presets are advisory. Repository instructions and task-specific evidence still win.
- Load only the selected preset file.
- Combine with detected Skills from `agent-team/skills/registry.md`.
- Escalate quality, review, and specialist gates when task risk requires it.
- Do not let a preset bypass human approval, testing, review, or safety policies.

---

## Optional Command

```bash
~/AgentCrew/bin/agentcrew preset --project .
```

This writes the selected preset to `.agent-state/project-preset.md`.
