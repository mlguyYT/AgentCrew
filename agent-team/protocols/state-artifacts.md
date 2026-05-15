# State Artifacts

## Purpose

State artifacts preserve current work context between agents and sessions.

They are project working state. They are not part of the reusable AgentCrew methodology.

---

## Folder Rule

Use:

```text
.agent-state/
```

Do not store project-specific state in:

```text
agent-team/
```

`agent-team/` is reusable methodology. `.agent-state/` is local project context.

---

## Recommended Files

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

Use only the files that are useful for the current project.

---

## File Purposes

```yaml
current-task.md:
  purpose: active task, acceptance criteria, lane, and owner

decisions.md:
  purpose: durable human or agent decisions with dates

handoff.md:
  purpose: compact current handoff between roles

test-report.md:
  purpose: latest Tester evidence

review-report.md:
  purpose: latest Reviewer findings

security-review-report.md:
  purpose: latest Security Reviewer findings

ux-design-review-report.md:
  purpose: latest UX / Design Reviewer findings

documentation-report.md:
  purpose: latest Documentation Agent findings

memory.md:
  purpose: short project context worth preserving between sessions
```

---

## Handoff Schema

Use the format from `agent-team/protocols/handoff-format.md`:

```md
### Context
- 1-3 bullets only.

### Decision
What was decided.

### Evidence
- Only facts needed by the next agent.

### Next Action
Exactly what the next agent should do.

### Open Questions
Only blockers.
```

---

## Current Task Schema

```md
# Current Task

## Title

## Lane
Fast Lane / Full Lane

## Risk
Low / Medium / High / Critical

## Owner
Developer / Tester / Reviewer / Specialist / Human

## Acceptance Criteria
- criterion

## Status
Current state.

## Next Action
Exactly what should happen next.
```

---

## Safety

State artifacts must not include:

- secrets
- tokens
- passwords
- private keys
- raw customer data
- sensitive production data
- long logs
- hidden reasoning traces

If a secret is discovered, follow `agent-team/policies/secrets-policy.md`.

---

## Git Policy

`.agent-state/` is usually gitignored.

If a project intentionally commits state artifacts, keep them short, factual, dated, and free of sensitive data.
