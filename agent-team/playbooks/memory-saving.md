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

If the repository needs committed memory, use a project-owned folder such as:

```text
docs/agent-memory/
```

If memory is local, private, or tool-specific, use the tool's memory store or a gitignored local folder.

Do not store project memory inside `agent-team/`; that folder is the reusable workflow package.

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
  - known risks
  - next steps
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
  -> remove secrets and noise
  -> write memory summary
  -> mark open questions
  -> tell the human where it was saved
```

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
