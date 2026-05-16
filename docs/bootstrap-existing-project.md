# Load AgentCrew In An Existing Project

## Purpose

Use this guide to apply AgentCrew to an existing repository without copying AgentCrew into that repository.

AgentCrew is Markdown-first. It should live outside the project and be loaded by the coding agent on demand.

---

## Step 1 - Place AgentCrew outside the project

Clone or place AgentCrew in a stable local path:

```bash
git clone git@github.com-mlguyyt:mlguyYT/AgentCrew.git ~/AgentCrew
```

Do not copy `AGENTS.md` or `agent-team/` into the target project unless you intentionally want a vendored snapshot.

---

## Step 2 - Load AgentCrew from the target project

From the target project, tell the coding agent:

```text
Load AgentCrew from ~/AgentCrew.

Read ~/AgentCrew/AGENTS.md and ~/AgentCrew/agent-team/.
Use Fast Lane by default.
Use Full Lane for risky work.
Do not merge pull requests.
Keep PRs small.
Load relevant Skills from ~/AgentCrew/agent-team/skills/registry.md.
```

Optional: create a tiny project-local adapter that points to `~/AgentCrew/AGENTS.md`. Do not duplicate the full AgentCrew package in the project.

---

## Step 3 - Ask an agent to inspect the external AgentCrew structure

Use:

```text
Load AgentCrew from ~/AgentCrew.
Run the AgentCrew health check using ~/AgentCrew/agent-team/checklists/agentcrew-health-check.md.
Report missing files, stale platform assumptions, and human-approval gaps.
Do not edit application code.
```

Fix missing AgentCrew files in the external AgentCrew repository before asking agents to perform product work.

---

## Step 4 - Run the first Fast Lane task

Start with a small, reversible task.

Example:

```text
Act as Developer Agent.
Load AgentCrew from ~/AgentCrew.
Use Fast Lane.
Make one small docs-only change in this project.
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
~/AgentCrew/agent-team/skills/registry.md
```

If a needed Skill is missing:

1. Create it in the external AgentCrew repository using `~/AgentCrew/agent-team/skills/authoring-guide.md`.
2. Register it in `~/AgentCrew/agent-team/skills/registry.md`.
3. Validate it using `~/AgentCrew/agent-team/playbooks/skill-validation.md`.

---

## Bootstrap Done Definition

Bootstrap is complete when:

- external `~/AgentCrew/AGENTS.md` exists
- external `~/AgentCrew/agent-team/` exists
- required roles, playbooks, templates, policies, and Skills registry exist
- any optional project-local adapter points to external AgentCrew files
- no required runtime, container platform, or custom service assumption remains
- human approval and no-autonomous-merge rules are present
- one small Fast Lane task has been validated
