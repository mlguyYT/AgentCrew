# Memory Saving Playbook

## Purpose

This playbook defines how agents should preserve useful project context between sessions without leaking secrets, bloating the repository, or turning temporary notes into false authority.

Memory is for durable context that helps future work:

- decisions made
- constraints discovered
- commands that worked or failed
- open follow-ups
- known risks
- accepted tradeoffs

Memory is not a replacement for source code, tests, issues, PRs, or human approval.

---

## When to save memory

Save memory when:

```yaml
save_when:
  - human asks to save progress
  - work pauses before completion
  - a significant decision is made
  - a recurring issue is diagnosed
  - a non-obvious command or setup detail is discovered
  - a rework loop reveals useful context
  - a handoff to another agent is likely
```

For small completed tasks, a PR description or test report is usually enough.

---

## Where to save memory

Use the human's preferred memory system if one exists.

Each target project must have separate memory.
AgentCrew must not mix memory across projects when it is used on multiple repositories at the same time.

For local session state, use the target project's own:

```text
.agent-state/
```

Do not save one project's state into another project's `.agent-state/`.

If the repository needs committed memory, use a project-owned folder such as:

```text
docs/agent-memory/
```

If memory is local, private, or tool-specific, use the tool's memory store or a gitignored local folder.

Do not store project memory inside `agent-team/`; that folder is the reusable workflow package.

Shared or committed memory must be team-neutral.
It should contain project knowledge, not personal workstation details.

---

## What to save

Include:

```yaml
memory_fields:
  - date
  - task or topic
  - current status
  - decisions
  - important files or areas
	  - commands run
	  - test results or limitations
	  - current repo status
	  - open untracked files that affect the task
	  - active cloud resources and teardown status
	  - current eval metrics when evaluation gates exist
	  - known risks
	  - next steps
	  - next safe action under project constraints
```

Use:

```text
agent-team/templates/memory-summary.md
```

---

## What not to save

Never save:

```yaml
forbidden:
  - secrets
  - API keys
  - tokens
  - passwords
  - private keys
  - private key paths
  - deploy-key paths
  - personal Git identity
  - personal email addresses
  - local machine paths
  - workstation-specific auth commands
  - raw customer data
  - sensitive production data
  - large logs
  - irrelevant terminal output
  - speculation presented as fact
```

If a secret is discovered, follow:

```text
agent-team/policies/secrets-policy.md
```

---

## Memory quality rules

Good memory is:

```yaml
good_memory:
  - short
  - factual
  - dated
  - tied to a task or decision
  - clear about unknowns
  - useful to a future agent
  - team-neutral if committed or shared
```

Bad memory is:

```yaml
bad_memory:
  - vague
  - oversized
  - duplicate of the PR
  - full of raw logs
  - mixed with secrets
  - written as permanent truth when it was only an assumption
```

---

## Save flow

```text
Identify durable context
  -> refresh against current branch, HEAD, validation, risks, cloud resources, untracked files, eval metrics, and next steps
  -> remove secrets and noise
  -> remove personal/local setup details
  -> preserve active project constraints and commit/push mode
  -> write memory summary
  -> mark open questions
  -> tell the human where it was saved
```

Before committing or updating shared memory, use:

```text
agent-team/checklists/shared-memory-refresh.md
```

---

## Optional session save utility

If AgentCrew is available outside the project, agents may save a local session checkpoint with:

```bash
~/AgentCrew/agent-team/tools/save-session.sh --project . --title "short title"
```

Use extra fields when useful:

```bash
~/AgentCrew/agent-team/tools/save-session.sh \
  --project . \
  --title "checkout validation work" \
  --summary "Checkout validation was updated and tests are partially complete." \
  --decision "Keep validation in the form service layer." \
  --next "Run focused checkout tests." \
  --note "Coverage tooling exists; target remains 70 percent or higher."
```

For a token-efficient resume checkpoint, use a structured checkpoint block:

```bash
~/AgentCrew/bin/agentcrew checkpoint \
  --project . \
  --title "checkout validation work" \
  --summary "Checkout validation was updated and tests are partially complete." \
  --decision "Keep validation in the form service layer." \
  --next "Run focused checkout tests." \
  --risk "Coverage baseline still needs verification." \
  --skill "Developer" \
  --validation "Focused tests pending."
```

Restore the latest checkpoint with:

```bash
~/AgentCrew/bin/agentcrew restore-session --project .
```

Checkpoint block rules live in:

```text
agent-team/protocols/checkpoint-blocks.md
```

By default, the utility writes to:

```text
PROJECT_ROOT/.agent-state/sessions/
```

To list saved checkpoints or show the latest one:

```bash
~/AgentCrew/agent-team/tools/list-sessions.sh --project .
~/AgentCrew/agent-team/tools/list-sessions.sh --project . --latest
```

If the command is run from a subdirectory inside a git repository, it automatically resolves the git repository root and saves there.
This keeps each project's checkpoints isolated even when AgentCrew is loaded from the same external `~/AgentCrew` checkout.

The utility captures short git state only: branch, head, status, diff stat, staged diff stat, and recent log.
It avoids saving absolute project paths, full diffs, secrets, raw customer data, sensitive production data, personal identifiers, private key paths, local auth commands, or long logs.

---

## Human boundary

The human decides whether project memory should be committed, edited, deleted, or treated as authoritative.

Agents may suggest memory entries.  
Agents must not treat their own memory as higher priority than repository instructions, source code, tests, or human direction.

---

## Done definition

Memory saving is complete when:

```yaml
done:
  - summary is short and factual
  - secrets are excluded
  - next steps are explicit
  - uncertainty is labeled
  - storage location is clear
```
