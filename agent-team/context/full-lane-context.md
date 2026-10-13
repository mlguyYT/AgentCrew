# Full Lane Context

## Use When

Use for high-risk, ambiguous, product, security, migration, infrastructure, or hard-to-rollback work.

## Load By Phase

### Planning

```text
agent-team/playbooks/full-lane.md
agent-team/playbooks/task-classification.md
agent-team/agents/product-manager.md
agent-team/skills/registry.md
```

Load Advisor and Idea Consultant only for rough ideas or product-direction questions.
Load Software Architect Agent and `architecture-decisions.md` only for significant boundaries, contracts, data ownership, dependencies, or quality attributes.
For idea-led delivery, load `idea-to-product.md`, prepare `executive-brief.md`, then stop at the CEO execution gate.

### Implementation

```text
agent-team/agents/developer.md
matching Skill files only
```

### Validation / Review

```text
agent-team/agents/tester.md
agent-team/agents/reviewer.md
```

### Triggered Gates Only

```text
agent-team/playbooks/lane-escalation.md
agent-team/playbooks/default-branch-merge.md
agent-team/playbooks/dependency-supply-chain.md
agent-team/playbooks/behavior-preserving-refactor.md
agent-team/playbooks/compatibility-rollout.md
```

Load only specialist agent files that match the work.

## Output Budget

Use full templates for human decision points. Otherwise keep handoffs compact and avoid repeating previous artifacts.
