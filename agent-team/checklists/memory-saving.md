# Memory Saving Checklist

## Purpose

Use this checklist before saving agent memory or handoff context.

---

## Save trigger

Confirm at least one is true:

- human requested memory saving
- work is paused
- decision context would be hard to rediscover
- setup or command knowledge is useful later
- another agent needs handoff context
- repeated rework revealed a pattern

---

## Content check

Memory includes:

- task or topic
- status
- decisions made
- files or areas touched
- commands run
- test results or limitations
- risks
- next steps

---

## Safety check

Memory does not include:

- secrets
- tokens
- passwords
- private keys
- raw customer data
- sensitive production data
- large logs
- irrelevant terminal output

---

## Quality check

Memory is:

- dated
- concise
- factual
- clear about assumptions
- useful to a future agent
- stored outside `agent-team/`

---

## Recommendation

If memory is useful for everyone, suggest committing it under a project-owned docs path.

If memory is private or temporary, keep it in the tool's private memory store or a gitignored local path.
