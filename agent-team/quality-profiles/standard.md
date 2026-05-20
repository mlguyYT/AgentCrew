# Standard Quality Profile

## Purpose

Use Standard for maintained products, startup teams, normal feature work, and most production repositories.

Standard is AgentCrew's default quality profile.

---

## Defaults

```yaml
profile: standard
recommended_for:
  - maintained product
  - startup team
  - production application
  - open-source project with users
default_lane: Fast Lane, Full Lane for high-risk work
default_output: normal
review_required: conditional
coverage_target: 70 percent when coverage tooling exists, document gap for human decision otherwise
```

---

## Required Gates

- Developer and Tester for implementation work
- Reviewer when risk is meaningful
- Product Manager when user-visible behavior, scope, compatibility, migration, or rollout changes
- Specialist Reviewer when specialist routing triggers
- dependency/supply-chain gate when dependency, lockfile, runtime, container, CI, or build-system files change
- integration-test need evaluated when behavior spans modules or external systems
- human approval before PR approval or merge

---

## Escalate To Strict When

- security, financial, data-loss, regulatory, or enterprise reliability risk is meaningful
- multiple teams or external customers depend on the behavior
- rollback is difficult
- quality gate override is requested
