# PR Preparation

## Purpose

PR preparation creates one compact packet for human review from AgentCrew state.

It helps product builders see the task, readiness, validation, reviews, risks, and pending human decisions without reading every handoff file.

---

## Run

From a target project:

```bash
~/AgentCrew/bin/agentcrew pr-pack
```

From anywhere:

```bash
~/AgentCrew/bin/agentcrew pr-pack --project /path/to/project
```

This creates or updates:

```text
.agent-state/pr-pack.md
```

Use `--dry-run` to preview and `--force` when intentionally replacing an existing packet.

---

## What It Checks

- current task, brief, work plan, and readiness status
- test, review, architecture, security, UX, and documentation reports
- pending human-only decisions
- git branch, default branch, HEAD, and worktree status when available
- risks and gaps that should be visible before approval

---

## Rules

- A PR packet is evidence, not approval.
- Agents may prepare the packet and suggested PR description.
- Only the human may approve the PR, accept risk, or merge.
- Missing validation or review evidence should be marked as a gap, not hidden.

See:

```text
agent-team/playbooks/pr-preparation.md
agent-team/templates/pr-pack.md
agent-team/checklists/pr-preparation.md
```
