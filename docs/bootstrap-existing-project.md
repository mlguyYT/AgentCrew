# Bootstrap Existing Project

## Purpose

Use this guide to add AgentCrew to an existing repository without adding platform dependencies or changing the project's application code.

AgentCrew is Markdown-first. A bootstrap should copy instructions, verify structure, and run one small Fast Lane task before expanding.

---

## Step 1 - Copy the core package

From this repository, copy:

```text
AGENTS.md
agent-team/
```

Example:

```bash
cp AGENTS.md /path/to/project/
cp -r agent-team /path/to/project/
```

Commit the copied files separately from application changes.

---

## Step 2 - Add optional tool adapters

Add adapters only for tools your team uses:

```text
.codex/AGENTS.md
.claude/CLAUDE.md
.cursor/rules/agent-team.md
.github/copilot-instructions.md
```

Adapters should point to `AGENTS.md` and `agent-team/`. Do not duplicate the whole workflow in every adapter.

Optional GitHub templates:

```text
.github/PULL_REQUEST_TEMPLATE.md
.github/ISSUE_TEMPLATE/
```

---

## Step 3 - Ask an agent to inspect the structure

Use:

```text
Read AGENTS.md.
Run the AgentCrew health check using agent-team/checklists/agentcrew-health-check.md.
Report missing files, stale platform assumptions, and human-approval gaps.
Do not edit application code.
```

Fix missing workflow files before asking agents to perform product work.

---

## Step 4 - Run the first Fast Lane task

Start with a small, reversible task.

Example:

```text
Act as Developer Agent.
Use Fast Lane.
Update one README sentence to confirm AgentCrew is installed.
Then act as Tester Agent and validate the docs-only change.
Do not merge.
```

This verifies that the project can move through:

```text
Developer -> Tester -> Human approval
```

---

## Step 5 - Add Skills as needed

Inspect the target repository and load matching Skills from:

```text
agent-team/skills/registry.md
```

If a needed Skill is missing:

1. Create it using `agent-team/skills/authoring-guide.md`.
2. Register it in `agent-team/skills/registry.md`.
3. Validate it using `agent-team/playbooks/skill-validation.md`.

---

## Bootstrap Done Definition

Bootstrap is complete when:

- `AGENTS.md` exists
- `agent-team/` exists
- required roles, playbooks, templates, policies, and Skills registry exist
- optional adapters point to canonical files
- no required runtime, container platform, or custom service assumption remains
- human approval and no-autonomous-merge rules are present
- one small Fast Lane task has been validated
