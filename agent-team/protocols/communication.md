# Agent Communication Protocol

## Purpose

Agents should communicate through compact artifacts, not long chat transcripts.

The goal is to preserve quality while reducing repeated context, hidden assumptions, and token waste.

---

## Core rule

```text
Agents do not pass full reasoning.
Agents pass compact artifacts.
```

An agent handoff should contain the minimum context needed by the next agent to act safely.

---

## Default message format

Every agent handoff must use:

```md
### Context
- 1-3 bullets only.

### Decision
What was decided.

### Evidence
Only the facts needed by the next agent.

### Next Action
Exactly what the next agent should do.

### Open Questions
Only blockers.
```

If a field does not apply, write `None`.

---

## Example

```md
## PM -> Developer Handoff

### Context
- Add project creation from dashboard.
- Backend already has `Project` model.
- Use Fast Lane.

### Decision
Implement one small PR for API + validation.

### Acceptance Criteria
- POST /projects creates project.
- Empty name returns validation error.
- Tests cover success and invalid input.

### Next Action
Developer implements backend endpoint.

### Open Questions
None.
```

---

## Shared artifacts

Agents should write or update artifacts instead of re-explaining work in chat.

Recommended project artifact folder:

```text
.agent-state/
  current-task.md
  decisions.md
  handoff.md
  test-report.md
  review-report.md
  security-review-report.md
  ux-design-review-report.md
  documentation-report.md
  memory.md
```

The next agent should read only the relevant artifact and source files.

Do not store reusable AgentCrew instructions in `.agent-state/`.
Do not store project-specific state in `agent-team/`.

Use `agent-team/protocols/state-artifacts.md` for the standard artifact schema.

---

## Handoff routing

Use compact handoffs at these boundaries:

```text
Idea Consultant -> Product Manager
Product Manager -> Developer
Developer -> Tester
Tester -> Developer
Tester -> Reviewer
Reviewer -> Developer
Reviewer -> Human
Security Reviewer -> Developer
UX / Design Reviewer -> Developer
Documentation Agent -> Developer
Documentation Agent -> Human
Human -> Developer
```

---

## Safety

Handoffs must not include:

- secrets
- tokens
- passwords
- private keys
- raw customer data
- sensitive production data
- long logs
- full reasoning traces

If a secret is discovered, follow:

```text
agent-team/policies/secrets-policy.md
```

---

## Related protocols

Use:

```text
agent-team/protocols/handoff-format.md
agent-team/protocols/token-discipline.md
```
