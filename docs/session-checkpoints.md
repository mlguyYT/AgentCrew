# Session Checkpoints

## Purpose

Session checkpoints preserve compact project-local context so a future AgentCrew session can resume without rereading long chat history.

They are explicit, local, and non-invasive. AgentCrew does not auto-commit checkpoint blocks by default.

---

## Save A Checkpoint

Use:

```bash
~/AgentCrew/bin/agentcrew checkpoint \
  --project . \
  --title "checkout validation" \
  --summary "Checkout validation was updated and focused tests are next." \
  --decision "Keep validation in the form service layer." \
  --next "Run focused checkout tests." \
  --risk "Coverage baseline still needs verification." \
  --skill "Developer" \
  --validation "Tests not run yet."
```

This writes a timestamped file under:

```text
.agent-state/sessions/
```

The file includes a compact `[agentcrew-context]` block for token-efficient restore.

---

## Save Without A Context Block

Use `save-session` for a normal session summary:

```bash
~/AgentCrew/bin/agentcrew save-session \
  --project . \
  --title "checkout validation" \
  --summary "Checkpoint saved before validation."
```

---

## Restore Latest Session

Use:

```bash
~/AgentCrew/bin/agentcrew restore-session --project .
```

This prints the latest session summary, decisions, remaining work, risks, validation, and checkpoint block when present.

Restore is read-only. It does not modify files.

---

## Restore A Specific File

```bash
~/AgentCrew/bin/agentcrew restore-session --project . --file .agent-state/sessions/20260522-120000-checkout-validation.md
```

---

## Safety

Checkpoint files must not include secrets, tokens, raw customer data, sensitive production data, long logs, personal identifiers, local machine paths, private key paths, deploy-key paths, workstation-specific auth commands, full diffs, or hidden reasoning traces.

Use:

```text
agent-team/protocols/checkpoint-blocks.md
agent-team/playbooks/memory-saving.md
agent-team/checklists/shared-memory-refresh.md
```

Final product direction, risk acceptance, PR approval, and merge remain human-only.
