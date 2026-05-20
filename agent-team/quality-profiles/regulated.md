# Regulated Quality Profile

## Purpose

Use Regulated when work has legal, compliance, privacy, safety, financial, contractual, or audit-trail requirements.

Regulated does not turn AgentCrew into a compliance system. It makes the agent workflow preserve evidence and human approval boundaries more explicitly.

---

## Defaults

```yaml
profile: regulated
recommended_for:
  - compliance-sensitive product
  - privacy-sensitive workflow
  - financial or contractual workflow
  - safety-critical behavior
  - audit-required release
default_lane: Full Lane
default_output: audit
review_required: true
coverage_target: 70 percent minimum when coverage tooling exists, with explicit human decision for gaps
```

---

## Required Gates

- Full Lane unless human explicitly scopes the work down to low-risk documentation or analysis
- Product Manager documents scope, acceptance criteria, rollout, and exclusions
- Tester records validation evidence and test limitations
- Reviewer records blocking issues, non-blocking risks, preserved legacy issues, test gaps, and product/rollout decisions
- Security Reviewer required for auth, data, permissions, infrastructure, dependency, runtime, CI, or build changes
- Documentation Agent required for public behavior, migration, release, or user-facing policy changes
- human decision queue required for every risk acceptance or quality gate override
- no autonomous merge or approval

---

## Evidence Rule

Keep evidence concise, dated, and team-neutral. Do not store secrets, raw customer data, sensitive production data, personal identifiers, or local machine paths.
