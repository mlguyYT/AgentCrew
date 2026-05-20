# Fast Lane Context

## Use When

Task is small, scoped, reversible, and low or medium risk.

## Required Files

```text
agent-team/agents/developer.md
agent-team/agents/tester.md
agent-team/playbooks/fast-lane.md
agent-team/playbooks/skill-loading.md
agent-team/skills/registry.md
agent-team/templates/compact-test-report.md
agent-team/templates/compact-handoff.md
```

## Conditional Files

```yaml
reviewer:
  load_when: meaningful risk, shared module, public API/protocol, dependency/runtime/config, large diff, tester uncertainty
  files:
    - agent-team/agents/reviewer.md
    - agent-team/templates/compact-review-report.md

product_manager:
  load_when: scope, behavior, compatibility, migration, rollout, or unclear acceptance criteria
  files:
    - agent-team/agents/product-manager.md
    - agent-team/templates/task.md

specialist:
  load_when: trigger appears in route-index or specialist-review-routing
  files:
    - relevant specialist agent only
    - relevant specialist template only
```

## Output Budget

- classification: 5 lines max
- handoff: 150 words max
- test report: compact by default
- review: triage first, full report only if meaningful findings exist
