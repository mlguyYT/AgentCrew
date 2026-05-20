# LLM Review Checklist

## Purpose

Use this checklist for LLM features, prompt changes, RAG, tool use, model configuration, and LLM safety reviews.

---

## Behavior

- [ ] expected output behavior is defined
- [ ] failure behavior is defined
- [ ] structured outputs are validated
- [ ] fallback behavior is documented
- [ ] cost, latency, and token constraints are considered

---

## Evaluation

- [ ] evals or golden cases cover important behavior
- [ ] regressions are checked
- [ ] hallucination risk is tested or documented
- [ ] prompt changes have before/after evidence when risk is meaningful

---

## Safety

- [ ] prompt injection risk is considered
- [ ] tool-call boundaries are explicit
- [ ] sensitive data handling is safe
- [ ] output is not trusted without validation where it affects state or users
- [ ] model/provider changes have rollout notes when production behavior changes

---

## Human Decision

Human approval is required for sensitive data use, model/provider changes in production, weakened guardrails, or accepted hallucination/safety risk.
