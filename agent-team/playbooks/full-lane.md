# Full Lane Playbook

## Purpose

Full Lane is the structured development workflow for important or risky work.

It adds more thinking before implementation and more quality control before human approval.

Use Full Lane when the cost of mistakes is high.

---

## Summary

```text
Idea
  -> Advisor
  -> Researcher Agent if evidence is needed
  -> Idea Consultant
  -> Product Manager
  -> Human direction and execution approval for idea-led delivery
  -> Developer
  -> Tester
  -> Reviewer
  -> Specialist Reviewer if needed
  -> Human approval
```

Full Lane is slower than Fast Lane, but safer.

---

## When to use Full Lane

Use Full Lane for:

```yaml
use_full_lane_for:
  - authentication
  - authorization
  - billing
  - payments
  - customer data
  - database migrations
  - infrastructure
  - CI/CD
  - deployment logic
  - public APIs
  - large refactors
  - high-impact product changes
  - security-sensitive work
```

---

## Full Lane roles

### Advisor

Evaluates whether the idea is worth pursuing and identifies major risks.

### Researcher Agent

Collects source-backed evidence only when feasibility or direction depends on external facts.

### Idea Consultant

Turns the idea into a structured idea brief.

### Product Manager

Creates MVP scope, tasks, acceptance criteria, priorities, and dependencies.

### Developer

Implements focused tasks.

### Tester

Validates behavior and acceptance criteria.

### Reviewer

Reviews quality, architecture, and risk.

### Specialist Reviewers

Security Reviewer, UX / Design Reviewer, Software Architect Agent, Documentation Agent, LLM Agent, Researcher Agent, and CNN Agent review their areas when the task touches them.

### Human / CEO

Approves material product direction, execution boundaries, consequential risk, release, PR, and merge. AgentCrew handles internal team coordination and routine reversible decisions.

---

## Full Lane gates

Full Lane has human approval gates.

```yaml
human_gates:
  direction_and_execution_approval:
    before: implementation
  pr_approval:
    before: merge
```

Combine direction, MVP scope, backlog, and execution approval when one decision is safe and clear. Split gates only for consequential architecture, elevated spend, unresolved product direction, or risk acceptance.

Agents may recommend approval, but cannot approve for the human.

---

## Full Lane steps

### Step 1 — Advisor evaluation

Advisor should produce:

```yaml
advisor_output:
  - recommendation
  - strengths
  - risks
  - suggested direction
  - scope reduction advice
```

Possible recommendations:

```yaml
recommendations:
  - proceed
  - refine
  - reject
```

When external evidence is needed, Researcher Agent supplies a compact evidence handoff before the idea brief is finalized.

---

### Step 2 — Idea Consultant brief

Idea Consultant should produce:

```yaml
idea_brief:
  - title
  - problem statement
  - target users
  - expected value
  - constraints
  - assumptions
  - risks
  - recommended MVP direction
  - open questions
```

---

### Step 3 — PM planning

Product Manager creates:

```yaml
product_plan:
  - MVP scope
  - out-of-scope items
  - epics
  - tasks
  - acceptance criteria
  - priorities
  - dependencies
  - risk levels
  - lane recommendation
```

Tasks must be small enough for focused PRs.

---

### Step 4 — Human direction and execution approval

AgentCrew presents a compact executive brief containing its recommendation, MVP scope, alternatives, risks, delivery slices, and cost boundary. The human approves, refines, pauses, or rejects it before implementation.

This prevents agents from building the wrong thing.

---

### Step 5 — Developer implementation

Developer implements one task at a time.

Rules:

```yaml
developer_rules:
  - one primary developer per PR
  - small PRs
  - no unrelated refactors
  - tests added or updated
  - no direct protected-branch pushes
```

---

### Step 6 — Tester validation

Tester validates:

```yaml
tester_checks:
  - acceptance criteria
  - relevant tests
  - regression risk
  - CI results if available
```

Failures route back to Developer.

---

### Step 7 — Reviewer review

Reviewer checks:

```yaml
reviewer_checks:
  - correctness
  - maintainability
  - architecture
  - security
  - test adequacy
  - scope control
```

Reviewer may mark ready for human review, but cannot approve as human.

For significant boundary, contract, data-ownership, runtime-dependency, or quality-attribute decisions, route through Software Architect Agent and `agent-team/playbooks/architecture-decisions.md`.

---

### Step 8 — Specialist review if needed

Use specialist reviewers when the task touches their area:

```yaml
specialist_reviewers:
  security_reviewer:
    use_for:
      - auth
      - permissions
      - secrets
      - sensitive data
      - dependency or infrastructure risk

  ux_design_reviewer:
    use_for:
      - UI
      - UX
      - accessibility
      - visual hierarchy
      - user-facing flows

  documentation_agent:
    use_for:
      - README
      - usage docs
      - examples
      - changelog
      - release notes
```

Specialist reviewers may request rework but may not approve as the human.

---

### Step 9 — Human PR approval

Human reviews final PR and decides:

```yaml
human_pr_decisions:
  - approve
  - request changes
  - close
  - split PR
```

Only human merges.

---

## Full Lane done definition

Full Lane work is done when:

```yaml
done:
  - idea was refined
  - scope was approved
  - implementation is complete
  - tests are documented
  - reviewer concerns are resolved
  - specialist reviewer concerns are resolved when required
  - human approves final PR
  - human merges if desired
```

---

## Agent instruction

When acting under Full Lane:

```text
Be structured.
Protect quality.
Document risks.
Keep tasks small.
Do not bypass human gates.
```
