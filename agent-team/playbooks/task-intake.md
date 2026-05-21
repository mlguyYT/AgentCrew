# Task Intake Playbook

## Purpose

Turn a plain user request into a compact project-local current task without making the user name AgentCrew, a role, a lane, or a Skill.

Task intake is the bridge between natural-language requests and the normal AgentCrew workflow.

---

## When To Use

Use task intake when:

```yaml
task_intake_when:
  - starting new work from a user request
  - resuming a request that has not been written into .agent-state/current-task.md
  - the agent needs a compact artifact before handing work to another role
  - the human wants the current AgentCrew route made visible
```

Do not use task intake to replace planning, testing, review, or human approval.

---

## Process

```yaml
intake_steps:
  - understand the requested outcome
  - classify the request using route-index and request-routing
  - choose lane, starting role, quality profile, Skills, and gates
  - create or update .agent-state/current-task.md
  - keep acceptance criteria provisional when the request is vague
  - continue with the selected role and lane
```

For command-line intake, use:

```bash
~/AgentCrew/bin/agentcrew start --project . --task "Fix the login validation bug"
```

Use `--dry-run` to preview the artifact and `--force` only when intentionally replacing the current task.

---

## Artifact Rule

Write project-specific task state to:

```text
.agent-state/current-task.md
```

Do not write current task state inside `agent-team/` or the AgentCrew checkout when AgentCrew is guiding an external project.

---

## Output Requirements

The current task should include:

```yaml
required_sections:
  - title
  - request
  - intent
  - lane
  - risk
  - quality profile
  - owner
  - workflow
  - acceptance criteria
  - status
  - next action
  - open questions
```

Use `agent-team/templates/current-task.md` as the canonical shape.

---

## Safety

Current task artifacts must not include secrets, tokens, raw customer data, sensitive production data, personal Git identity, personal email, local machine paths, private key paths, deploy-key paths, long logs, or hidden reasoning traces.

If the request needs a human-only decision, update `.agent-state/human-decisions.md` using `agent-team/playbooks/human-decision-queue.md`.
