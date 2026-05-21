# Acceptance Criteria Playbook

## Purpose

Turn a vague request into a small, testable task brief before implementation starts.

Acceptance criteria make AgentCrew easier for product builders because users can ask for an outcome naturally while agents preserve scope, testability, and human decision boundaries.

---

## When To Use

Use this playbook when:

```yaml
use_when:
  - the request is vague
  - acceptance criteria are missing
  - user-visible behavior changes
  - Product Manager is selected or triggered
  - Developer needs a clearer implementation target
  - Tester needs explicit validation points
```

For tiny obvious fixes, keep acceptance criteria brief.

---

## Process

```yaml
criteria_process:
  - restate the requested outcome in one sentence
  - identify user/operator visible behavior
  - define in-scope behavior
  - define out-of-scope behavior
  - write observable acceptance criteria
  - identify test evidence needed
  - identify review, specialist, and human decision gates
  - list only blocking open questions
```

---

## Criteria Quality Bar

Good acceptance criteria are:

- observable
- testable
- scoped to one task or PR
- phrased as behavior, not implementation preference
- clear about errors, empty states, permissions, and compatibility when relevant
- clear about what must not change

Avoid criteria that are:

- vague, such as "make it better"
- impossible to validate
- bundled across unrelated workflows
- silently changing public behavior without a human decision

---

## Command

Use the optional task brief command:

```bash
~/AgentCrew/bin/agentcrew brief --project . --task "Fix the login validation bug"
```

Use `--dry-run` to preview and `--force` only when intentionally replacing `.agent-state/task-brief.md`.

---

## Artifact

Write project-specific task briefs to:

```text
.agent-state/task-brief.md
```

Use:

```text
agent-team/templates/task-brief.md
```

Do not write task briefs into `agent-team/` or the AgentCrew checkout when AgentCrew is guiding another project.
