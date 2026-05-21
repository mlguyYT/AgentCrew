# Work Planning

## Purpose

Work planning turns a routed AgentCrew request into a PR-sized implementation sequence.

It helps product builders avoid oversized agent changes and gives teams a compact artifact that shows what should happen first, what needs review, and where human decisions are required.

---

## Create A Work Plan

From a target project:

```bash
~/AgentCrew/bin/agentcrew plan --task "Add OAuth login"
```

This creates:

```text
.agent-state/work-plan.md
```

Use `--dry-run` to preview and `--force` only when intentionally replacing the current plan.

---

## What It Contains

- selected recipe, lane, risk, quality profile, and workflow
- planning assumptions
- PR-sized phases
- owner, goal, acceptance, validation, and gates per phase
- human decisions and risks
- next action

---

## Rules

- Keep each phase small enough for focused review.
- Separate implementation, validation, documentation, release, and human decision work.
- Put human-only decisions before dependent implementation.
- Human approval remains final.

See:

```text
agent-team/playbooks/work-planning.md
agent-team/templates/work-plan.md
agent-team/checklists/work-planning.md
```
