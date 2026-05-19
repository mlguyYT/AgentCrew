# Integration Test Escalation

## Purpose

Use this checklist when unit tests alone may not be enough to validate behavior after modularization or cross-system changes.

---

## Escalate To Integration Tests When

Recommend or add integration tests when:

- [ ] core services are extracted
- [ ] behavior is distributed across modules
- [ ] reconnect, retry, timer, or cleanup logic exists
- [ ] state is stored outside process memory
- [ ] production behavior depends on multiple components interacting
- [ ] external services are involved
- [ ] messaging, sockets, queues, databases, caches, filesystems, or distributed state are involved

---

## Validation Guidance

Integration validation should cover:

- component boundaries
- persistence or external state behavior
- retry and cleanup behavior
- compatibility paths
- failure handling
- the user/operator-visible behavior that unit tests cannot prove

If integration tests are too expensive for the current task, document the gap and ask for human decision before treating the work as low risk.
