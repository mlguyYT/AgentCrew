# Research Context

## Use When

The task needs source-backed investigation, current facts, option comparison, or uncertainty reduction before planning or implementation.

## Required Files

```text
agent-team/agents/researcher-agent.md
agent-team/templates/compact-research-report.md
agent-team/checklists/research-quality.md
agent-team/skills/professional/researcher-pro.md
```

## Source Budget

```yaml
source_budget:
  default_sources: 3-5
  prefer_primary_sources: true
  cite_only_decision_relevant_sources: true
  no_long_quotes: true
  stop_when_decision_ready: true
```

## Expand When

Use `agent-team/templates/research-report.md` only when the decision is high impact, evidence conflicts, or the human asks for full research.
