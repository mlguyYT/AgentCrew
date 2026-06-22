# Project Constraints

## Purpose

Project constraints are standing instructions for one target project. They capture rules that should survive long sessions, handoffs, and agent restarts.

Use:

```text
.agent-state/project-constraints.md
```

Template:

```text
agent-team/templates/project-constraints.md
```

---

## Load Rule

If `.agent-state/project-constraints.md` exists, read it before:

- implementation
- cloud or deployment operations
- documentation or public artifact changes
- generated file handling
- commit or push preparation
- review
- handoff or memory saving

Do not ask the human to restate constraints that are already recorded.

---

## No-Commit Mode

When the constraint file says commits or pushes are not allowed:

- do not commit
- do not push
- do not prepare a default-branch merge
- repeat the active no-commit/no-push mode in work summaries
- record any requested commit or push as a human decision

Only an explicit human instruction for that action can override the mode. A general approval to continue work is not commit or push approval.

---

## Public/Private Boundary

Use the constraint file to preserve project boundaries:

- public repository work
- private local notes
- separate private workspaces
- ignored runtime state
- sensitive wording that must not appear in public artifacts

When an artifact or feature does not clearly belong in the public repository, pause and classify it with `agent-team/playbooks/artifact-classification.md` or `agent-team/playbooks/public-private-boundary.md`.

---

## Memory

When saving progress, include only compact constraint-relevant state:

- current repo status
- active cloud resources
- open untracked files
- current eval metrics
- next safe action

Do not save secrets, raw customer data, private paths, local auth commands, long logs, or hidden reasoning.

