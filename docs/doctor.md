# AgentCrew Doctor

## Purpose

`agentcrew doctor` checks whether an AgentCrew checkout is usable and whether the current environment can see it.

Use it after installation, after changing global loaders, or when an agent does not seem to apply AgentCrew automatically.

---

## Run

From the AgentCrew checkout:

```bash
~/AgentCrew/bin/agentcrew doctor
```

From another project, point to the external checkout if needed:

```bash
~/AgentCrew/bin/agentcrew doctor --root ~/AgentCrew
```

---

## What It Checks

The doctor checks:

- core AgentCrew files such as `AGENTS.md`, `agent-team/`, route index, playbooks, protocols, and Skills registry
- required Agent role files
- required output templates, including task routing and human decision queue templates
- Claude Code, Codex, OpenClaw, and Hermes Agent global loader registrations
- local tool availability such as `git`, the project detector, the task classifier, context manifest, project preset selector, task intake, task brief, work plan, readiness check, PR packet preparation, session save/restore, and the status dashboard
- setup docs such as installation, automatic loading, loader management, project detection, project presets, task classifier, context manifest, session checkpoints, task intake, acceptance criteria, work planning, implementation readiness, PR preparation, release management, support triage, status dashboard, and human decision queue docs
- whether AgentCrew's own repository ignores its local `.agent-state/`
- whether AgentCrew is external to the current project when run from a target project
- whether always-loaded and hot-path files stay within token budget warnings
- whether any tracked file grew more than 10% in word count since the last doctor run, using `.agent-state/doctor-budget-history.tsv` as per-checkout history

Warnings are informational. Failures indicate missing required files or an invalid AgentCrew root.

---

## Expected Result

A healthy setup exits with no failures:

```text
Summary:
  failures: 0
```

Warnings can still appear when a supported tool is not installed, when a loader has not been registered, or when a development checkout differs from the globally registered checkout.

For example, if you develop AgentCrew in one folder but registered another checkout, doctor may warn that loaders point elsewhere. That is not blocking unless you expected the current checkout to be the active installation.

---

## Fix Common Issues

If global loaders are missing, run:

```bash
~/AgentCrew/bin/agentcrew install
```

If a loader points to an old checkout, reinstall with the intended root:

```bash
/path/to/AgentCrew/bin/agentcrew install --root /path/to/AgentCrew
```

To remove AgentCrew-managed loader blocks, preview first:

```bash
~/AgentCrew/bin/agentcrew uninstall --dry-run
```

If required files are missing, update or reclone AgentCrew.

If a target project has no `.agent-state/`, that is normal until session memory is saved.
