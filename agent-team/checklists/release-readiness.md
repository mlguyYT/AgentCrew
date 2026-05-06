# Release Readiness Checklist

## Purpose

This checklist helps decide whether a change is ready to release.

---

## Required

- [ ] PR is approved by human
- [ ] required checks passed or were explicitly waived by human
- [ ] risks are documented
- [ ] rollback plan is understood
- [ ] no high/critical review findings remain
- [ ] deployment notes exist if needed

---

## For database changes

- [ ] migration reviewed
- [ ] rollback strategy documented
- [ ] data loss risk considered
- [ ] compatibility considered

---

## For API changes

- [ ] backward compatibility considered
- [ ] clients considered
- [ ] documentation updated if needed

---

## For UI changes

- [ ] main user flow checked
- [ ] screenshots or manual verification included if useful
- [ ] accessibility concerns considered

---

## For infrastructure changes

- [ ] config impact documented
- [ ] secrets handled safely
- [ ] deployment commands reviewed
- [ ] destructive actions avoided unless approved

---

## Release decision

```yaml
release_decision:
  - ready
  - hold
  - needs_human_decision
```
