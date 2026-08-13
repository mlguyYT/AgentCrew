# Compatibility Rollout

## Purpose

This playbook defines the default pattern for protocol, API, auth, config, and client/server compatibility changes.

The goal is to improve safety without silently breaking existing users or operators.

---

## Runtime Contract

- Identify existing public, protocol, configuration, auth, and client contracts.
- Prefer a secure default with an explicit, temporary compatibility mode when needed.
- Test both the intended path and any retained compatibility path.
- Document rollout, affected consumers, rollback, and legacy-mode removal.
- Stop for human approval before accepting breakage, data risk, or insecure compatibility.

---

## Use This For

Use this playbook when a change touches:

```yaml
compatibility_triggers:
  - public API behavior
  - protocol messages
  - authentication or authorization behavior
  - client/server compatibility
  - production configuration defaults
  - migrations with rollout risk
  - behavior relied on by external operators or integrations
```

---

## Recommended Pattern

Prefer:

```yaml
compatibility_pattern:
  - secure default
  - explicit legacy compatibility flag if needed
  - documented rollout note
  - tests for secure path
  - tests for legacy compatibility path
  - clear plan to remove legacy mode later
```

Legacy compatibility must be explicit.
Do not keep insecure compatibility silently.

---

## Human Approval Required

The human must approve:

- changing public behavior
- enabling legacy insecure compatibility
- accepting compatibility breakage
- accepting migration or data-loss risk
- removing legacy mode

---

## Output

Document:

```yaml
rollout_note:
  - secure default
  - compatibility flag or mode
  - affected clients or operators
  - tests for secure behavior
  - tests for legacy behavior
  - removal plan
  - human decision needed
```
