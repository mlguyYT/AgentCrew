# Skill: LLM Pro

## Purpose

Use this skill for large language model application work: prompts, RAG, embeddings, tool use, model selection, evaluations, guardrails, observability, and LLM safety.

---

## Applies when

Use this skill when work involves:

- prompts or system messages
- RAG, embeddings, retrieval, or vector search
- tool calling, function calling, agent loops, or structured output
- model/provider selection or fallback behavior
- LLM evaluation, golden sets, or regression tests
- hallucination, prompt injection, data leakage, or LLM safety risk

---

## Detection triggers

```yaml
triggers:
  text:
    - LLM
    - prompt
    - system message
    - RAG
    - embeddings
    - vector search
    - tool calling
    - function calling
    - structured output
    - evals
    - hallucination
    - prompt injection
    - model selection
    - context window
  files:
    - "prompts/**"
    - "evals/**"
    - "**/*prompt*"
    - "**/*rag*"
```

---

## Instructions

- Treat model output as untrusted until validated.
- Keep prompts versionable and testable when they affect product behavior.
- Prefer explicit schemas for structured output.
- Define fallback behavior for model/provider failures.
- Separate prompt problems from retrieval, tool, and application-state problems.
- Do not send secrets, raw customer data, or sensitive production data to external models without explicit human approval and policy support.

---

## Testing guidance

- Add or update evals for meaningful behavior changes.
- Include negative and adversarial cases when prompt injection or tool misuse is plausible.
- Test structured output parsing and failure paths.
- Record model/provider, prompt version, and evaluation limitations when relevant.

---

## Review checklist

- prompt injection risk considered
- hallucination handling defined
- sensitive data boundaries respected
- tool-call boundaries explicit
- structured output validated
- eval coverage fits risk
- model/provider rollout risk documented

---

## Anti-patterns

Avoid:

- relying on prompt wording alone for security
- trusting model output for state changes without validation
- changing production model/provider without rollout notes
- accepting hallucination risk without human decision
- hiding eval gaps behind anecdotal examples
