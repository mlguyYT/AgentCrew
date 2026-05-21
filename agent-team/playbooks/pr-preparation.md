# PR Preparation Playbook

## Purpose

Prepare a compact pull-request packet from AgentCrew state before human review.

PR preparation helps product builders see what changed, what was validated, which reviews happened, and what still needs a human decision without reading every intermediate artifact.

---

## When To Use

Use this playbook when:

```yaml
use_when:
  - implementation is complete or nearly complete
  - Tester has produced validation evidence
  - Reviewer or specialist review is needed before human approval
  - the human asks for a PR summary, release packet, or approval packet
  - work is ready to hand from agents to the human
```

Do not use this playbook to approve or merge work. It prepares evidence only.

---

## Inputs

Read project-local state when present:

```text
.agent-state/current-task.md
.agent-state/task-brief.md
.agent-state/work-plan.md
.agent-state/readiness-report.md
.agent-state/test-report.md
.agent-state/review-report.md
.agent-state/security-review-report.md
.agent-state/ux-design-review-report.md
.agent-state/documentation-report.md
.agent-state/human-decisions.md
```

Also inspect the git branch, default branch, HEAD, and worktree status when the target project is a git repository.

---

## Required Checks

Before marking a PR packet ready for human review, confirm:

```yaml
required:
  - current task or clear request exists
  - readiness is not blocked
  - validation evidence is present or the gap is documented
  - review evidence is present when risk requires review
  - specialist evidence is present when triggered
  - pending human-only decisions are surfaced
  - risks and test gaps are explicit
  - no agent claims to approve or merge as the human
```

---

## Command

Use:

```bash
~/AgentCrew/bin/agentcrew pr-pack --project .
```

Use `--dry-run` to preview and `--force` only when replacing `.agent-state/pr-pack.md`.

---

## Artifact

Write project-specific PR packets to:

```text
.agent-state/pr-pack.md
```

Use:

```text
agent-team/templates/pr-pack.md
```
