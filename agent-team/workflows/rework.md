# Workflow: Rework Loop

## Purpose
Handle failures and route fixes correctly.

---

## Flow

```text
Failure
  -> Rework request
  -> Developer
  -> PR update
  -> Re-validation
```

---

## Sources of rework

- Tester failure
- Reviewer request
- Specialist reviewer request
- Human feedback
- CI failure

---

## Rules

```yaml
rules:
  - same developer owns rework
  - same PR branch reused
  - do not expand scope
```

---

## Rework steps

1. Identify issue
2. Create rework request
3. Developer fixes
4. Update PR
5. Re-run validation
6. Re-review if needed

---

## Output

```yaml
output:
  - updated PR
  - resolved issues
```
