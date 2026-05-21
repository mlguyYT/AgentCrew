# Release Management Playbook

## Purpose

Prepare release readiness evidence and a human-facing release recommendation.

This playbook helps product builders ship with clearer validation, rollout, rollback, and approval context while keeping final release decisions human-only.

---

## When To Use

Use this playbook when:

```yaml
use_when:
  - request mentions release, ship, deploy, version bump, changelog, release notes, rollout, rollback, or merge readiness
  - PR is ready for final human review and release impact should be summarized
  - default-branch merge readiness or release readiness needs a compact packet
  - deployment or rollout is being prepared but not autonomously approved
```

---

## Required Inputs

Prefer project-local artifacts when present:

```text
.agent-state/current-task.md
.agent-state/task-brief.md
.agent-state/work-plan.md
.agent-state/readiness-report.md
.agent-state/pr-pack.md
.agent-state/test-report.md
.agent-state/review-report.md
.agent-state/security-review-report.md
.agent-state/documentation-report.md
.agent-state/human-decisions.md
```

Also inspect changed release files such as changelog, version files, package files, lockfiles, CI config, migration notes, and deployment notes when relevant.

---

## Release Checks

```yaml
release_checks:
  - validation evidence is present or the gap is explicit
  - review and specialist evidence is present when triggered
  - changelog or release notes match shipped behavior when needed
  - default-branch merge readiness is checked when preparing a merge
  - dependency and supply-chain gate ran when package, lock, runtime, container, CI, or build files changed
  - compatibility and rollout notes exist for API, protocol, auth, config, migration, or client/server changes
  - rollback or remediation path is understood
  - human-only decisions are recorded and unresolved items block release recommendation
```

---

## Output

Write project-specific release reports to:

```text
.agent-state/release-report.md
```

Use:

```text
agent-team/templates/release-report.md
```

---

## Decision Options

```yaml
release_decision:
  - ready_for_human_release_review
  - hold_for_fixes
  - needs_human_decision
```

Agents may recommend one of these outcomes. Only the human may approve merge, release, deployment, or risk acceptance.
