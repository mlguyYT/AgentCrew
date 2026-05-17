# Load AgentCrew In An Existing Project

## Purpose

Use this guide to apply AgentCrew to an existing repository without copying AgentCrew into that repository.

AgentCrew is Markdown-first. It should live outside the project and be registered once with supported coding agents.

---

## Step 1 - Place AgentCrew outside the project

Clone or place AgentCrew in a stable local path:

```bash
git clone https://github.com/mlguyYT/AgentCrew.git ~/AgentCrew
~/AgentCrew/bin/agentcrew install
```

Do not copy `AGENTS.md` or `agent-team/` into the target project unless you intentionally want a vendored snapshot.

---

## Step 2 - Ask for the outcome from the target project

From the target project, ask normally:

```text
Fix the login form so empty email shows a validation message.
```

AgentCrew should read its own instructions, classify the task, choose the lane, role, and Skills, and stop where human approval is required.

Optional: create a tiny project-local adapter that points to `~/AgentCrew/AGENTS.md`. Do not duplicate the full AgentCrew package in the project.

---

## Step 3 - Ask an agent to inspect the external AgentCrew structure

Use:

```text
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
Make one small docs-only change in this project.
Let AgentCrew classify the task, choose the role and lane, validate the change, and stop before merge.
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
- `~/AgentCrew/bin/agentcrew status` shows the expected registration
- required roles, playbooks, templates, policies, and Skills registry exist
- any optional project-local adapter points to external AgentCrew files
- no required runtime, container platform, or custom service assumption remains
- human approval and no-autonomous-merge rules are present
- one small Fast Lane task has been validated
