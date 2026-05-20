# Strict Quality Profile

## Purpose

Use Strict for enterprise teams, high-impact product areas, shared platforms, production infrastructure, critical APIs, and complex refactors.

Strict favors confidence and review depth over speed.

---

## Defaults

```yaml
profile: strict
recommended_for:
  - enterprise product team
  - production platform
  - critical user flow
  - shared service or module
  - large refactor
default_lane: Full Lane for medium-or-higher risk
default_output: audit
review_required: true
coverage_target: 70 percent minimum when coverage tooling exists, with explicit gap decision if unavailable
```

---

## Required Gates

- Product Manager verifies acceptance criteria for behavior changes
- Tester runs focused and broad validation where available
- Reviewer required for implementation changes
- specialist review required for any matching trigger
- dependency/supply-chain gate required for dependency/runtime/container/CI/build changes
- integration tests required when behavior spans modules or external systems and tooling exists
- compatibility rollout required for API, protocol, auth, config, or client/server behavior changes
- human decision queue required for unresolved risk acceptance

---

## Escalate To Regulated When

- legal, compliance, privacy, safety, financial reporting, medical, or contractual evidence requirements apply
- audit trail or formal approval evidence is required
