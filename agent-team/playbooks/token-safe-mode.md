# Token-Safe Mode

## Purpose

Token-Safe Mode keeps AgentCrew quality gates while reducing repeated context, broad file loading, and oversized outputs.

Use it by default unless the human asks for exhaustive detail or the task is high-risk enough to require full artifacts.

---

## Loading Rule

```text
AGENTS.md
  -> agent-team/context/route-index.md
  -> one context profile
  -> one role file
  -> matching skills only
  -> triggered gates only
  -> current output template only
```

Do not load all roles, all playbooks, all templates, docs, examples, or structure files during normal target-project work.

---

## Expansion Triggers

Expand context only when:

- risk becomes medium/high/critical
- security, data, migration, compatibility, dependency, runtime, CI, or default-branch merge gates trigger
- specialist routing is confirmed
- tests fail or coverage is below threshold
- product scope or human decision is unclear
- the human asks for full detail

---

## Output Budgets

```yaml
classification: 5 lines max
handoff: 150 words max
fast_lane_test_report: 10 lines max
fast_lane_review: 7 meaningful findings max
specialist_report: 500 words max unless high risk
research_sources: 3-5 by default
```

---

## Review Triage

Use two-phase review:

```text
triage review
  -> no meaningful issues: compact pass
  -> meaningful issues: full review report
```

---

## Do Not Repeat

Do not repeat repository background, full task history, acceptance criteria, long logs, full files, or hidden reasoning if already available in artifacts or source files.
