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
- [ ] default-branch merge readiness is documented
- [ ] committed shared state is team-neutral if state artifacts are committed

---

## For database changes

- [ ] migration reviewed
- [ ] rollback strategy documented
- [ ] data loss risk considered
- [ ] compatibility considered

---

## For dependency, runtime, container, CI, or build-system changes

- [ ] ecosystem audit or security check ran when available
- [ ] remaining dependency paths are understood
- [ ] forced or breaking audit fixes were human-approved
- [ ] overrides or resolutions are documented
- [ ] tests were rerun after dependency changes

---

## For API changes

- [ ] backward compatibility considered
- [ ] secure default documented
- [ ] legacy compatibility flag documented if needed
- [ ] removal plan exists for legacy mode if used
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
