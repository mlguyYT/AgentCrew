# Specialist Review Routing

## Purpose

This playbook tells agents when to involve a specialist reviewer.

Specialist reviewers and specialist agents are used only when their area is touched. They do not replace Developer, Tester, Reviewer, Product Manager, or human approval.

Use lazy loading: during initial classification, use this routing table only. Load a specialist role file and template only after the trigger is confirmed.

---

## Routing Table

```yaml
security_reviewer:
  role_file: agent-team/agents/security-reviewer.md
  template: agent-team/templates/security-review-report.md
  triggers:
    - authentication
    - authorization
    - permissions
    - secrets
    - customer data
    - sensitive data
    - payments or billing
    - dependency changes
    - lockfile changes
    - runtime changes
    - container changes
    - CI or build-system changes
    - infrastructure permissions
    - public API exposure
    - input handling with injection risk

ux_design_reviewer:
  role_file: agent-team/agents/ux-design-reviewer.md
  template: agent-team/templates/ux-design-review-report.md
  triggers:
    - UI changes
    - user-facing flows
    - onboarding
    - forms
    - navigation
    - accessibility
    - responsive behavior
    - visual layout
    - copy that changes user understanding

documentation_agent:
  role_file: agent-team/agents/documentation-agent.md
  template: agent-team/templates/documentation-report.md
  triggers:
    - README changes
    - installation docs
    - usage docs
    - examples
    - changelog
    - release notes
    - public API behavior
    - migration notes

llm_agent:
  role_file: agent-team/agents/llm-agent.md
  template: agent-team/templates/llm-report.md
  triggers:
    - prompt design
    - system messages
    - RAG
    - embeddings
    - vector search
    - tool calling
    - function calling
    - structured output
    - model selection
    - LLM evaluations
    - hallucination risk
    - prompt injection
    - LLM safety

researcher_agent:
  role_file: agent-team/agents/researcher-agent.md
  template: agent-team/templates/research-report.md
  triggers:
    - source-backed research
    - uncertain facts
    - technology comparison
    - standards or regulations
    - current or latest information
    - market or product research
    - external citations
    - primary-source evidence

cnn_agent:
  role_file: agent-team/agents/cnn-agent.md
  template: agent-team/templates/cnn-report.md
  triggers:
    - computer vision
    - CNN
    - convolutional neural networks
    - image classification
    - object detection
    - segmentation
    - image datasets
    - augmentation
    - model training
    - inference optimization

skill_validator:
  role_file: agent-team/agents/skill-validator.md
  template: agent-team/templates/skill-validation-report.md
  triggers:
    - new Skill added
    - Skill changed
    - Skill registry changed
    - Skill category reorganized
    - Skill trigger changed
```

---

## Fast Lane Use

In Fast Lane, add a specialist only when the trigger is directly present.
Use compact outputs unless the specialist finds meaningful risk.

Example:

```text
Developer -> Tester -> Security Reviewer -> Human
```

Do not add specialist review for unrelated areas.

---

## Full Lane Use

In Full Lane, identify needed specialist review during Product Manager planning and confirm again after implementation.

Example:

```text
Product Manager -> Developer -> Tester -> Reviewer -> UX / Design Reviewer -> Human
```

If scope changes during implementation, rerun this routing check.

---

## Multiple Specialists

Use more than one specialist only when multiple areas are touched.

Example:

```text
Checkout redesign with payment copy:
  - Security Reviewer for payment/data risk
  - UX / Design Reviewer for checkout flow
  - Documentation Agent for release notes or usage docs
  - LLM Agent for prompt, RAG, eval, or model behavior risk
```

Keep reports separate so findings stay actionable.

---

## Non-Triggers

Do not involve a specialist only because:

- the role exists
- the PR is small but unrelated to the specialist area
- a reviewer has style preferences
- docs mention a feature but no docs behavior changed

---

## Handoff Rule

Specialist rework routes back to the original Developer unless the issue is docs-only and the Documentation Agent is explicitly assigned to update docs. Researcher Agent output may route to Product Manager when the next step is a product or strategy decision.

Human approval remains required.
