# Review Context

## Use When

The task is PR review, quality review, merge readiness, or rework verification.

## Required Files

```text
agent-team/agents/reviewer.md
agent-team/playbooks/pr-process.md
agent-team/checklists/code-review.md
agent-team/templates/compact-review-report.md
agent-team/skills/registry.md
```

## Escalate To Full Review

Load `agent-team/templates/review-report.md` only when there are blocking issues, meaningful risks, test gaps, product decisions, or rollout decisions.

## Conditional Review Gates

```yaml
supply_chain: dependency, lockfile, runtime, container, CI, or build-system changes
default_branch_merge: preparing merge to default branch
refactor: behavior-preserving refactor or behavior ambiguity
compatibility: protocol, API, auth, config, migration, or client/server compatibility
specialist: security, UX, docs, LLM, research, or CNN trigger
```

## Output Budget

- pass with no issues: 5 bullets max
- findings: 7 meaningful findings max in Fast Lane
- no style nits unless they create real risk
