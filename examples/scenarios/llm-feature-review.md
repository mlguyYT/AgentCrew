# LLM Feature Review

## User Prompt

```text
Review this new RAG answer flow for hallucination risk, prompt injection, tool-call safety, structured output validation, and eval coverage.
```

## Expected AgentCrew Routing

```yaml
starting_role: LLM Agent
quality_profile: standard or strict depending on product risk
required_skills:
  - llm-pro
next_roles:
  - Developer if implementation changes are needed
  - Tester if eval or regression validation is needed
  - Security Reviewer if data leakage or prompt injection risk is meaningful
  - Human
```

## Expected Artifacts

```text
.agent-state/llm-report.md when durable review context helps
.agent-state/test-report.md when evals or regression checks run
.agent-state/review-report.md when implementation changes are reviewed
```

## Human Boundary

Agents may recommend mitigations.
The human approves product behavior, model-risk acceptance, customer-data policy, and release.
