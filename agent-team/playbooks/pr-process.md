# Pull Request Process

## Purpose

This playbook defines the standard PR process for the AgentCrew workflow.

The PR process ensures that code changes are:

- small
- traceable
- tested
- reviewed
- human-approved

---

## Golden rule

```text
Agents may create or update PRs.
Agents may not merge PRs.
```

---

## Standard PR flow

```text
Developer
  -> Pull Request
  -> Tester
  -> Reviewer
  -> Specialist Reviewer if needed
  -> Human approval
  -> Human merge
```

For low-risk Fast Lane work:

```text
Developer
  -> Pull Request
  -> Tester
  -> Reviewer when risk is meaningful
  -> Product Manager when scope or product behavior changes
  -> Human approval
```

Reviewer is optional only for genuinely low-risk work.

---

## PR ownership

Each PR must have one primary Developer Agent owner.

```yaml
pr_ownership:
  primary_developer_required: true
  multiple_primary_developers_allowed: false
  rework_returns_to_original_developer: true
```

Supporting agents may comment or validate, but should not create competing changes on the same branch unless explicitly instructed.

---

## Branch rules

Agents must not work directly on protected branches.

Protected branches usually include:

```yaml
protected_branches:
  - main
  - master
  - develop
  - release/*
```

Recommended branch format:

```text
agent/<role>/<task-id>
```

Examples:

```text
agent/developer/task-001
agent/developer-backend/task-042
agent/docs/update-readme
```

---

## PR title format

Recommended:

```text
[Agent][TASK-ID] Short description
```

Example:

```text
[Agent][TASK-001] Add project creation endpoint
```

---

## PR description requirements

Every PR should include:

```md
## Summary
What changed.

## Task
Task ID or description.

## Acceptance Criteria
- [x] criterion 1
- [x] criterion 2

## Tests
Commands run and results.

## Risk
Low / Medium / High

## Notes for Reviewer
Anything important to inspect.
```

Use:

```text
agent-team/templates/pr-description.md
```

---

## Developer responsibilities

Developer must:

```yaml
developer_responsibilities:
  - implement task
  - keep changes focused
  - preserve modular clean architecture
  - update tests when needed
  - keep coverage at or above 70 percent when coverage tooling exists
  - preserve legacy behavior during refactors unless the task explicitly includes behavior change
  - run dependency and supply-chain checks when dependency, lockfile, runtime, container, CI, or build-system files change
  - prepare PR description
  - document tests run
  - mention limitations
```

Developer must not:

```yaml
developer_forbidden:
  - merge PR
  - bypass review
  - hide failing tests
  - commit secrets
  - make unrelated changes
```

---

## Tester responsibilities

Tester must:

```yaml
tester_responsibilities:
  - validate acceptance criteria
  - run relevant tests
  - run coverage checks when available
  - flag coverage below 70 percent
  - recommend integration tests when behavior spans modules or external systems
  - document results
  - request rework if behavior fails
```

Tester may not merge.

---

## Reviewer responsibilities

Reviewer must:

```yaml
reviewer_responsibilities:
  - check correctness
  - check scope
  - check maintainability
  - check architecture fit
  - check modularity and clean architecture boundaries
  - check security concerns
  - check test adequacy
  - check coverage is at least 70 percent when tooling exists
  - separate blocking issues, non-blocking risks, preserved legacy issues, test gaps, product or rollout decisions, and next implementation phase
```

Reviewer may mark ready for human review.

Reviewer may not merge.

---

## Specialist reviewer responsibilities

Specialist reviewers are used only when the PR touches their area.

```yaml
specialist_reviewers:
  security_reviewer:
    checks:
      - auth
      - permissions
      - secrets
      - data handling
      - dependency or infrastructure risk

  ux_design_reviewer:
    checks:
      - user flow
      - accessibility
      - visual hierarchy
      - responsive behavior
      - screenshots or manual evidence

  documentation_agent:
    checks:
      - docs match behavior
      - examples are current
      - changelog or release notes are updated if needed
      - links and file paths are current
```

Specialist reviewers may request rework.
Specialist reviewers may not approve as the human or merge.

---

## Human responsibilities

Human decides:

```yaml
human_responsibilities:
  - approve final PR
  - request changes
  - merge
  - reject or close PR
  - accept security, data-loss, migration, compatibility, or public-behavior risk
  - approve force-push or shared-history rewrite
```

---

## Default-Branch Merge Readiness

Before any default-branch merge, use:

```text
agent-team/playbooks/default-branch-merge.md
```

Do not assume the default branch name.
Detect it from remote metadata or ask the human.

---

## Dependency And Supply-Chain Gate

When package, lockfile, package manager, runtime, container, CI, or build-system files change, use:

```text
agent-team/playbooks/dependency-supply-chain.md
```

Avoid forced or breaking audit fixes unless the human explicitly approves.

---

## PR labels

Recommended labels:

```yaml
labels:
  - agent-generated
  - needs-test
  - needs-review
```

Optional labels:

```yaml
risk_labels:
  - risk-low
  - risk-medium
  - risk-high

role_labels:
  - backend
  - frontend
  - infra
  - docs
  - test
```

---

## When to split a PR

Split PR if:

```yaml
split_if:
  - too many unrelated files changed
  - multiple features included
  - refactor mixed with behavior change
  - reviewer cannot understand scope quickly
  - risky change can be isolated
```

---

## PR done definition

A PR is ready for human approval when:

```yaml
ready_for_human:
  - acceptance criteria addressed
  - implementation is modular and architecture fit is acceptable
  - relevant tests run or limitation documented
  - coverage is at least 70 percent when coverage tooling exists, or exception is documented
  - tester passed or provided acceptable report
  - reviewer passed if required
  - Product Manager checked scope or behavior change if required
  - specialist reviewer passed if required
  - supply-chain gate passed if dependency, runtime, container, CI, or build-system files changed
  - default-branch merge readiness documented if preparing merge
  - no critical unresolved comments
  - PR description is clear
```

---

## Agent instruction

When working with PRs:

```text
Make changes visible.
Keep scope small.
Document tests honestly.
Route failures to rework.
Never merge.
```
