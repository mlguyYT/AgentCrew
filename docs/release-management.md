# Release Management

## Purpose

Release management gives AgentCrew a clear owner for preparing release readiness evidence.

The Release Manager can summarize validation, review, changelog, rollout, rollback, and human-decision gaps, but cannot approve, merge, deploy, or accept risk as the human.

---

## Use When

Use Release Manager when a task involves:

- release readiness
- version bumps
- changelog or release notes
- default-branch merge preparation
- deployment preparation
- rollout or rollback planning

---

## Outputs

Project-specific release reports should live at:

```text
.agent-state/release-report.md
```

Use:

```text
agent-team/agents/release-manager.md
agent-team/playbooks/release-management.md
agent-team/templates/release-report.md
agent-team/checklists/release-readiness.md
```

---

## Human Boundary

Agents may prepare release evidence and recommendations.

Only the human may approve final release, merge to the default branch, deploy production, or accept security, data, migration, compatibility, or rollback risk.
