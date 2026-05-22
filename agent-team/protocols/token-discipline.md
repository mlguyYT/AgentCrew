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
  - route_before_loading_details: true
  - lazy_load_specialists: true
  - compact_templates_by_default_in_fast_lane: true
  - direct_answer_mode_for_questions: true
  - max_direct_answer: 10_lines_unless_user_asks_for_depth
  - max_classification: 5_lines
  - max_handoff_length: 150_words
  - max_review_comment: 7_meaningful_findings_in_fast_lane
  - max_specialist_report: 500_words_unless_high_risk
  - max_research_sources_default: 3_to_5
  - max_test_report: commands_plus_pass_fail_plus_failures_only
```

---

## Direct Answer Mode

Use this for questions, explanations, and advice when the user has not asked for code changes, inspection, review, validation, commit, push, or saved state.

Rules:

- do not load role, lane, Skill, template, docs, or examples
- do not create `.agent-state/` artifacts
- do not run tools unless the answer depends on current repository or external facts
- answer from available context and keep it concise
- ask or offer to implement only when the user needs action

---

## Practical guidance

Do:

- cite files and line numbers when useful
- summarize changed behavior
- include commands and pass/fail results
- load only the routed context profile, selected role, matching skills, triggered gates, and current template
- include only blockers in open questions
- write or update shared artifacts

Do not:

- load every AgentCrew playbook, role, template, or skill by default
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
Use compact templates in Fast Lane unless risk requires full reports.

The next agent should read the relevant artifact instead of asking for a recap.

Use `agent-team/protocols/state-artifacts.md` for artifact schemas.

---

## Review comments

Review comments should be at most 7 meaningful findings in Fast Lane and at most 10 findings in Full Lane unless the human asks for exhaustive review.

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
