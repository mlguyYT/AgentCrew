# Master Workflow

## Purpose

This document defines how all agents, services, and runtime components work together as one startup-style software development system.

The system is designed to be:

- fast enough for startup iteration
- structured enough to keep software quality high
- human-controlled at all important approval gates
- local-first on Ubuntu 24.04
- scalable later through specialized agents

---

# 1. System Goal

The system creates a team of containerized agents that help develop software projects through GitHub pull requests.

The human remains the final approver.

The system must support:

```yaml
goals:
  - short development cycles
  - high software quality
  - small PRs
  - fast rework
  - local execution
  - Kubernetes-managed workers
  - Docker-isolated agents
  - OpenClaw runtime support
  - GitHub PR workflow
  - human approval before merge
```

---

# 2. Core Agents

The core agents are:

```yaml
core_agents:
  advisor:
    purpose: evaluate idea direction and risk

  idea_consultant:
    purpose: refine raw idea into structured idea brief

  product_manager:
    purpose: turn idea brief into executable backlog

  developer:
    purpose: implement code and open/update PRs

  tester:
    purpose: validate behavior and acceptance criteria

  reviewer:
    purpose: review quality, architecture, and risk

  orchestrator:
    purpose: enforce workflow and route tasks

  agent_coordinator:
    purpose: launch runtime containers/jobs

  github_integration:
    purpose: map GitHub PR and CI events to workflow events

  ci_execution:
    purpose: run repeatable build/test/lint/typecheck commands
```

---

# 3. Human Authority

The human owns final decisions.

The system must enforce these human-only gates:

```yaml
human_only_gates:
  concept_approval:
    from: idea_brief_ready
    to: concept_approved

  backlog_approval:
    from: backlog_ready
    to: backlog_approved

  pr_approval:
    from: ready_for_human_review
    to: human_approved

  merge:
    from: human_approved
    to: merged
```

Agents may recommend approval.  
Agents may not replace approval.

---

# 4. Main Workflow

The full end-to-end workflow:

```text
Human idea
  -> Advisor Agent
  -> Idea Consultant Agent
  -> Human concept approval
  -> Product Manager Agent
  -> Human backlog approval
  -> Developer Agent
  -> Tester Agent
  -> Reviewer Agent
  -> Human PR approval
  -> Human merge
```

For startup speed, this workflow can be shortened using Fast Lane.

---

# 5. Workflow States

## Idea states

```yaml
idea_states:
  - idea_submitted
  - advisor_reviewing
  - idea_consulting
  - idea_brief_ready
  - concept_approved
  - concept_rework_needed
```

## Planning states

```yaml
planning_states:
  - pm_framing
  - pm_task_breakdown
  - backlog_ready
  - backlog_approved
  - planning_rework_needed
```

## Delivery states

```yaml
delivery_states:
  - task_assigned
  - implementation_in_progress
  - pr_opened
  - testing_in_progress
  - review_in_progress
  - rework_requested
  - ready_for_human_review
  - human_changes_requested
  - human_approved
  - merged
```

---

# 6. Default Startup Operating Model

Default mode should be:

```yaml
default_mode: fast_lane
```

Use Full Lane only when needed.

The startup rule:

```text
Use the smallest process that safely protects the current work.
```

---

# 7. Risk-Based Lane Selection

```yaml
low_risk:
  lane: fast_lane
  flow:
    - developer
    - tester
    - human

medium_risk:
  lane: fast_lane_or_full_lane
  flow:
    - product_manager
    - developer
    - tester
    - reviewer
    - human

high_risk:
  lane: full_lane
  flow:
    - advisor
    - idea_consultant
    - product_manager
    - developer
    - tester
    - reviewer
    - human

critical_risk:
  lane: full_lane_with_human_decision
  flow:
    - advisor
    - idea_consultant
    - human_decision
    - product_manager
    - human_backlog_approval
    - developer
    - tester
    - specialist_reviewer
    - human
```

---

# 8. Pull Request Ownership

Each PR must have exactly one primary Developer Agent owner.

```yaml
pr_ownership:
  one_primary_developer: true
  rework_returns_to_original_developer: true
  tester_may_request_rework: true
  reviewer_may_request_rework: true
  human_may_request_rework: true
  agents_may_merge: false
```

---

# 9. Rework Rule

All implementation rework routes back to the same Developer Agent owner.

```text
Tester failure
  -> Orchestrator
  -> Original Developer Agent
  -> Same PR branch
```

```text
Reviewer change request
  -> Orchestrator
  -> Original Developer Agent
  -> Same PR branch
```

```text
Human change request
  -> Orchestrator
  -> Developer or Reviewer depending on request
```

---

# 10. Codex Master Implementation Rules

When Codex implements this system, it must:

1. preserve human-only gates
2. keep Fast Lane as default
3. keep PRs small
4. route rework to original Developer Agent
5. never add autonomous merge
6. never grant agents branch-protection bypass
7. keep secrets placeholder-driven
8. keep local Ubuntu/k3s compatibility
9. support agent specialization
10. document every runtime assumption
