# Token Discipline

## Purpose

Agents should minimize repeated context while preserving enough evidence for safe handoffs, testing, review, and human decisions.

---

## Rules

```yaml
token_discipline:
  - do_not_repeat_repository_background_unless_changed
  - do_not_restate_full_task_history
  - link_to_files_instead_of_pasting_content
  - use_templates
  - use_diffs_or_summaries_not_full_files
  - max_handoff_length: 200_words
  - max_review_comment: 10_bullets
  - max_test_report: commands_plus_pass_fail_plus_failures_only
```

---

## Practical guidance

Do:

- cite files and line numbers when useful
- summarize changed behavior
- include commands and pass/fail results
- include only blockers in open questions
- write or update shared artifacts

Do not:

- paste full files
- paste long logs
- narrate every step already visible in artifacts
- repeat the same acceptance criteria in every message
- include hidden reasoning traces
- use chat as the permanent source of truth

---

## Shared artifact rule

Prefer artifacts over chat:

```text
.agent-state/current-task.md
.agent-state/decisions.md
.agent-state/handoff.md
.agent-state/test-report.md
.agent-state/review-report.md
.agent-state/security-review-report.md
.agent-state/ux-design-review-report.md
.agent-state/documentation-report.md
.agent-state/memory.md
```

Only update the artifact that changed.

The next agent should read the relevant artifact instead of asking for a recap.

Use `agent-team/protocols/state-artifacts.md` for artifact schemas.

---

## Review comments

Review comments should be at most 10 bullets.

Each finding should include:

- severity
- affected file
- issue
- required change

Avoid low-value style comments.

---

## Test reports

Test reports should include only:

- commands run
- pass/fail result
- failures
- limitations
- recommendation

Do not paste full test logs unless the failure cannot be understood without them.
