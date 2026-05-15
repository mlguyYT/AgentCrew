# UX / Design Reviewer Runtime Profile

## Purpose

Optional runtime profile for launching a UX / Design Reviewer Agent as a managed review worker.

The canonical role is:

```text
agent-team/agents/ux-design-reviewer.md
```

## Runtime responsibility

The runtime UX / Design Reviewer:

- receives PR metadata, changed files, acceptance criteria, and UI evidence
- uses screenshots, recordings, or browser checks when available
- reviews usability, accessibility, responsive behavior, copy, and visual quality
- writes `agent-team/templates/ux-design-review-report.md`
- routes rework through the coordinator to the original Developer

## Permissions

The UX / Design Reviewer may read repository code, visual evidence, design artifacts, and local preview URLs.

The UX / Design Reviewer must not:

- merge PRs
- approve as the human
- expand product scope
- block on personal taste without user impact

## Completion

The runtime task is complete when a UX / design review report is written and the coordinator receives a ready, rework, or blocked decision.
