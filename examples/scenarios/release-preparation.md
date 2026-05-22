# Release Preparation

## User Prompt

```text
Prepare this PR for release. Check the changelog, summarize validation, note rollback risk, and tell me what still needs human approval.
```

## Expected AgentCrew Routing

```yaml
starting_role: Release Manager
recipe: release
next_roles:
  - Tester if validation evidence is missing
  - Reviewer if release risk is meaningful
  - Documentation Agent if changelog or release notes need updates
  - Human
```

## Expected Artifacts

```text
.agent-state/pr-pack.md
.agent-state/release-report.md
.agent-state/human-decisions.md when approval or risk acceptance is pending
```

## Release Focus

- validation evidence
- review and specialist evidence
- changelog or release notes
- rollout and rollback notes
- default-branch merge readiness
- dependency or supply-chain gate when package/runtime/build files changed

## Human Boundary

Release Manager may prepare evidence and recommendation.
Only the human may approve release, deploy, merge, or risk acceptance.
