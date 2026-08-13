# Software Architecture

AgentCrew treats architecture as a conditional specialist concern, not a mandatory phase for every task.

Use Software Architect Agent when a decision changes important boundaries, contracts, data ownership, runtime dependencies, or quality attributes. Small changes should continue through Fast Lane without architecture ceremony.

## Route

```text
Architecture decision
  -> Software Architect Agent
  -> Product Manager if product scope changes
  -> Human decision
  -> Developer after approval
  -> Tester
  -> Reviewer
  -> Software Architect Agent if implementation needs conformance review
  -> Human
```

## Artifacts

```text
agent-team/agents/software-architect-agent.md
agent-team/skills/professional/software-architecture.md
agent-team/playbooks/architecture-decisions.md
agent-team/checklists/architecture-review.md
agent-team/templates/architecture-report.md
```

Project-specific architecture review state may live in:

```text
.agent-state/architecture-report.md
```

After human approval, teams may adapt the decision into their existing committed ADR or architecture-documentation convention.

## Principle

Architecture guidance should make design decisions explicit and testable while remaining proportionate. Prefer existing patterns and the simplest design that meets current quality requirements. Add distribution, abstraction, or infrastructure only when concrete scaling, ownership, isolation, reliability, or delivery needs justify it.
