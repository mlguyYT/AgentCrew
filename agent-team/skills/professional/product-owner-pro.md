# Skill: Professional Product Owner

## Purpose

Use this skill for product ownership, Product Owner planning, backlog shaping, prioritization, and value-focused acceptance criteria.

This skill can be used by Product Manager, Advisor, Idea Consultant, Developer, Tester, and Reviewer agents when a task needs product ownership judgment.

---

## Applies when

Use this skill when work involves:

- Product Owner or PO work
- product ownership
- product goal definition
- backlog creation or ordering
- acceptance criteria
- stakeholder tradeoffs
- user value
- scope decisions
- roadmap slicing
- release readiness from a product perspective
- deciding what is in or out of scope

---

## Detection triggers

Load this skill if the task or repo contains:

```yaml
triggers:
  text:
    - Product Owner
    - PO
    - product ownership
    - product goal
    - Product Goal
    - product backlog
    - backlog
    - acceptance criteria
    - stakeholder
    - prioritize
    - prioritization
    - roadmap
    - MVP
    - value
    - scope
  files:
    - "agent-team/templates/task.md"
    - "agent-team/templates/product-plan.md"
    - ".agent-state/current-task.md"
    - ".agent-state/decisions.md"
    - ".agent-state/handoff.md"
    - "docs/roadmap.md"
```

---

## Instructions

When applying Product Owner judgment:

- Start with the user, the problem, and the expected value.
- Define or clarify the Product Goal before ordering work.
- Convert vague ideas into small, testable backlog items.
- Make acceptance criteria observable and tied to user outcomes.
- Order work by value, risk reduction, learning, urgency, and dependency constraints.
- Keep one accountable product decision-maker visible for priority conflicts.
- Separate MVP scope from later enhancements.
- Surface tradeoffs clearly when scope, time, quality, or risk compete.
- Protect the team from unclear or constantly shifting priorities.
- Use stakeholder input as evidence, but do not turn priority into a committee decision.
- Escalate to the human for final product direction, backlog approval for large work, and any risk tradeoff.

---

## Testing guidance

For Product Owner work, validation should check whether the plan can be executed and verified:

- acceptance criteria are specific enough for Tester to validate
- each task can fit in a small focused PR
- user-facing behavior is described in outcome terms
- out-of-scope items are explicit
- dependencies and human approval gates are named
- risks are classified as low, medium, high, or critical
- success can be inspected through tests, demos, metrics, or review artifacts

No automated test command is required for planning-only work. If the Product Owner work changes product behavior, the resulting Developer task should include relevant test expectations.

---

## Review checklist

Reviewer should check:

- Product Goal is clear or the absence is called out
- target user and user problem are explicit
- backlog items are ordered by value and risk, not just effort
- acceptance criteria are testable
- MVP scope is small enough for Fast Lane or intentionally routed to Full Lane
- stakeholder and user evidence is separated from assumptions
- human-only decisions are not made by an agent
- security, data, billing, or infrastructure tradeoffs are escalated
- open questions are blockers only
- handoff to Developer is compact and actionable

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - treating PO as a committee
  - writing backlog items with no user outcome
  - prioritizing by loudest stakeholder only
  - hiding assumptions inside acceptance criteria
  - mixing MVP work with future roadmap items
  - approving final product direction as an agent
  - accepting security or data-risk tradeoffs without human approval
  - creating large vague tasks that cannot be tested
  - skipping out-of-scope decisions
  - changing priorities without explaining user or business impact
```

---

## Research basis

This skill is based on public Product Owner guidance from:

- The Scrum Guide, 2020: https://en.wikisource.org/wiki/The_Scrum_Guide_(2020)
- Atlassian Product Owner guidance: https://www.atlassian.com/agile/product-management/product-owner

---

## Output note

If relevant, include:

```md
## Skills Applied
- product-owner-pro
```
