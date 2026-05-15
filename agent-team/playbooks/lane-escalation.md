# Lane Escalation

## Purpose

This playbook defines when agents should move work between Fast Lane and Full Lane after the task has started.

Fast Lane keeps small work moving. Full Lane protects risky work with more planning and review.

---

## Escalate To Full Lane

Escalate if any of these appear during discovery, implementation, testing, or review:

```yaml
escalate_to_full_lane_if:
  - authentication is touched
  - authorization is touched
  - billing or payments are touched
  - customer data is touched
  - sensitive data handling changes
  - database migration is added
  - production infrastructure changes
  - CI/CD or deployment logic changes
  - public API behavior changes
  - rollback becomes difficult
  - task becomes vague or product-heavy
  - PR becomes too large
  - tests reveal broad regression risk
  - reviewer finds architecture risk
  - security reviewer finds unresolved data or access risk
```

Escalation means pausing implementation long enough to create or update scope, acceptance criteria, risks, and review requirements.

---

## De-Escalate To Fast Lane

De-escalate only when the risky scope has been removed or clarified.

```yaml
deescalate_to_fast_lane_if:
  - risky scope was removed
  - task is isolated and reversible
  - no customer data, auth, billing, migration, or infrastructure remains
  - acceptance criteria are clear
  - human confirms lightweight handling
```

Do not de-escalate only to move faster.

---

## How To Escalate

Use this handoff:

```md
## Developer -> Product Manager Handoff

### Context
- Fast Lane task discovered higher risk.

### Decision
Escalate to Full Lane.

### Evidence
- The change now touches <risk area>.

### Next Action
Product Manager should define scope, acceptance criteria, review needs, and human approval gate.

### Open Questions
Only blockers.
```

---

## How To De-Escalate

Use this handoff:

```md
## Product Manager -> Developer Handoff

### Context
- Risky scope was removed or clarified.

### Decision
Proceed in Fast Lane.

### Evidence
- Remaining task is isolated, reversible, and low risk.

### Next Action
Developer should implement the focused task and hand off to Tester.

### Open Questions
None.
```

---

## Human Boundary

Critical-risk work always needs explicit human decision before continuing.

Agents may recommend lane changes, but they may not accept security, data, payment, or production-risk tradeoffs for the human.
