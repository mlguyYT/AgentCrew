# Skill: Researcher Pro

## Purpose

Use this skill for source-backed research, evidence summaries, option comparison, and uncertainty handling.

---

## Applies when

Use this skill when work involves:

- uncertain facts
- technology or vendor comparison
- standards, regulations, or public API behavior
- market or product research
- current or latest information
- external citations
- high-impact decisions that need evidence

---

## Detection triggers

```yaml
triggers:
  text:
    - research
    - investigate options
    - compare
    - source-backed
    - citations
    - latest
    - current
    - standard
    - regulation
    - market research
    - primary source
```

---

## Source Budget

```yaml
source_budget:
  default_sources: 3-5
  prefer_primary_sources: true
  summarize_sources: true
  no_long_quotes: true
  stop_when_decision_ready: true
```

## Instructions

- Define the research question before collecting evidence.
- Prefer primary sources for technical, legal, security, standards, API, or product claims.
- Check dates when recency matters.
- Separate facts, assumptions, inferences, and recommendations.
- State confidence and limitations.
- Keep findings tied to the decision the human or next agent must make.

---

## Testing guidance

Research is validated by evidence quality, not code execution.

- Verify claims against cited sources.
- Cross-check important facts when possible.
- Identify stale, vendor-biased, or secondary evidence.
- Document unavailable or uncertain information.

---

## Review checklist

- question is clear
- sources are cited
- primary sources preferred
- facts and assumptions separated
- dates checked when relevant
- confidence stated
- limitations explicit
- next action clear

---

## Anti-patterns

Avoid:

- presenting assumptions as facts
- using stale sources for current decisions
- citing low-quality summaries when primary sources exist
- over-researching low-impact decisions
- making the final human decision inside the research report
