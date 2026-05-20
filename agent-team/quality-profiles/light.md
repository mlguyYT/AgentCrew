# Light Quality Profile

## Purpose

Use Light for solo builders, prototypes, documentation-only work, small experiments, and low-risk internal changes.

Light keeps momentum high while preserving the non-negotiable AgentCrew safety rules.

---

## Defaults

```yaml
profile: light
recommended_for:
  - solo builder
  - prototype
  - docs-only update
  - tiny low-risk fix
  - throwaway experiment
default_lane: Fast Lane
default_output: brief
review_required: risk_based
coverage_target: 70 percent when coverage tooling exists, document gap otherwise
```

---

## Required Gates

- human approval remains final
- no autonomous merge
- no secrets
- focused change scope
- relevant focused test or documented test limitation
- coverage check when coverage tooling already exists

---

## Escalate Out Of Light When

- auth, billing, customer data, migration, infrastructure, deployment, dependency, runtime, container, CI, or build-system files are touched
- public API, protocol, compatibility, or rollout behavior changes
- the task grows beyond a small focused change
- reviewer, tester, or human identifies meaningful risk
