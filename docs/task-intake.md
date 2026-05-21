# Task Intake

## Purpose

Task intake lets AgentCrew turn a normal user request into a compact current-task artifact for the target project.

Users can still just ask for the outcome. The intake flow is for agents and teams that want the current route, owner, risk, and quality profile written down before work continues.

---

## Start A Task

From a target project:

```bash
~/AgentCrew/bin/agentcrew start --task "Fix the login form so empty email shows a validation message"
```

This creates:

```text
.agent-state/current-task.md
```

The artifact includes the request, intent, lane, risk, quality profile, workflow recipe, starting owner, workflow, provisional acceptance criteria, status, next action, and open questions.

---

## Preview Without Writing

```bash
~/AgentCrew/bin/agentcrew start --dry-run --task "Add OAuth login"
```

---

## Replace The Current Task

By default, AgentCrew refuses to overwrite an existing current task.

Use `--force` only when intentionally replacing it:

```bash
~/AgentCrew/bin/agentcrew start --force --task "Update the dashboard filters"
```

If the old task should be preserved first, save a session checkpoint before replacing it.

For clearer scope and acceptance criteria, use `agentcrew brief`.

---

## Rules

- Task state belongs in the target project's `.agent-state/` folder.
- AgentCrew must not store current task state inside `agent-team/`.
- Acceptance criteria may be provisional when the request is vague.
- Human approval remains final.
- Do not store secrets, raw customer data, personal identifiers, local paths, private key paths, or long logs.

See:

```text
agent-team/playbooks/task-intake.md
agent-team/templates/current-task.md
agent-team/protocols/state-artifacts.md
```
