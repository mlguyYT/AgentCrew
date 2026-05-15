# Handoff Format

## Purpose

This file defines the standard compact handoff artifact between agents.

Use this format in chat, comments, or `.agent-state/` files.

---

## Standard handoff

```md
## <Sender> -> <Receiver> Handoff

### Context
- bullet 1
- bullet 2
- bullet 3

### Decision
Decision or current state.

### Evidence
- fact 1
- fact 2

### Next Action
Exactly what the next agent should do.

### Open Questions
- blocker 1
```

---

## Optional sections

Use only when helpful:

```md
### Acceptance Criteria
- criterion 1
- criterion 2

### Files
- path 1
- path 2

### Commands
- command: pass/fail
```

Do not add optional sections by default.

---

## Length limits

```yaml
limits:
  max_handoff_length: 200_words
  context: 1_to_3_bullets
  open_questions: blockers_only
```

---

## Good handoff

```md
## Tester -> Developer Handoff

### Context
- Fast Lane task for `/healthz`.
- Unit test command ran.

### Decision
Rework required.

### Evidence
- `pytest tests/test_health.py` failed.
- Expected JSON body, got plain text.

### Next Action
Return JSON `{ "status": "ok" }` and rerun the test.

### Open Questions
None.
```

## Specialist handoff

```md
## Security Reviewer -> Developer Handoff

### Context
- PR touches authentication.

### Decision
Rework required.

### Evidence
- Token refresh path has no expired-session test.

### Next Action
Add the missing test or document why it cannot be tested.

### Open Questions
None.
```

---

## Bad handoff

Avoid:

- full task history
- copied source files
- raw terminal logs
- speculation
- unrelated repository background
- hidden reasoning
