# GitHub Setup Guide

## Purpose

This guide explains how to configure a GitHub repository to support the Agent Team workflow.

---

## Recommended branch protection

Protect the default branch, usually:

```text
main
```

Recommended settings:

```yaml
branch_protection:
  require_pull_request_before_merging: true
  require_approvals: true
  require_status_checks: optional_but_recommended
  require_conversation_resolution: true
  restrict_force_pushes: true
  restrict_deletions: true
```

---

## Required human approval

Agents may prepare PRs and review them.

Agents should not merge.

Configure the repository so that a human maintainer is required before merge.

---

## Recommended labels

Create labels:

```yaml
workflow_labels:
  - agent-generated
  - agent-task
  - needs-planning
  - needs-test
  - needs-review
  - rework

risk_labels:
  - risk-low
  - risk-medium
  - risk-high
  - risk-critical

role_labels:
  - advisor
  - idea-consultant
  - product-manager
  - developer
  - tester
  - reviewer

lane_labels:
  - fast-lane
  - full-lane
```

---

## Issue templates

The included issue templates support:

```yaml
templates:
  - feature_request
  - bug_report
  - agent_task
  - rework_request
  - documentation
```

---

## PR template

The PR template ensures every change includes:

```yaml
required_pr_context:
  - summary
  - task
  - lane
  - acceptance criteria
  - tests
  - risk
  - reviewer focus
  - human approval reminder
```

---

## CODEOWNERS

Uncomment and replace the examples in:

```text
.github/CODEOWNERS
```

Example:

```text
* @my-org/core
/agent-team/ @my-org/agent-workflow-maintainers
/.github/ @my-org/repo-admins
/docs/ @my-org/docs
```

---

## Suggested first labels command

Using GitHub CLI:

```bash
gh label create agent-generated --color 7057ff --description "Created or assisted by an agent"
gh label create agent-task --color 0e8a16 --description "Task for agent workflow"
gh label create needs-test --color fbca04 --description "Needs tester validation"
gh label create needs-review --color fbca04 --description "Needs reviewer validation"
gh label create rework --color d73a4a --description "Requires rework"
gh label create fast-lane --color c5def5 --description "Fast Lane workflow"
gh label create full-lane --color 5319e7 --description "Full Lane workflow"
```

---

## Suggested first repository rule

```text
No agent-generated PR should be merged without human approval.
```
