# Skill Registry Guidance

Use this file only when Skill matching is ambiguous, when adding Skills, or when reviewing Skill selection behavior. Normal routing should load `agent-team/skills/registry.md` first and keep this file unloaded unless needed.

---

## Explicit skill syntax

Tasks may declare skills:

```md
## Skills
- python-pro
- fastapi
```

When explicit skills are present, load those files.

---

## Automatic detection examples

### Example 1

Task:

```text
Fix validation in a FastAPI endpoint.
```

Load:

```text
agent-team/skills/languages/python-pro.md
agent-team/skills/frameworks/fastapi.md
```

### Example 2

Changed files:

```text
src/components/Button.tsx
package.json
```

Load:

```text
agent-team/skills/frontend/react.md
agent-team/skills/languages/typescript-pro.md
```

### Example 3

Changed files:

```text
infra/k8s/deployment.yaml
infra/k8s/service.yaml
```

Load:

```text
agent-team/skills/platform/kubernetes.md
```

### Example 4

Task:

```text
Review this PR for risk, tests, and maintainability.
```

Load:

```text
agent-team/skills/professional/reviewer-pro.md
```

### Example 5

Task:

```text
Act as PO and turn this idea into a small backlog item with acceptance criteria.
```

Load:

```text
agent-team/skills/professional/product-owner-pro.md
```

---

## Skill priority

More specific skills override broader skills.

```yaml
priority_examples:
  fastapi_over_python:
    broader: python-pro
    specific: fastapi

  react_over_general_frontend:
    broader: frontend
    specific: react

  kubernetes_over_general_devops:
    broader: devops
    specific: kubernetes

  react_over_typescript_for_components:
    broader: typescript-pro
    specific: react

  product_owner_over_general_product_planning:
    broader: product_manager_role
    specific: product-owner-pro

  professional_reviewer_over_general_review:
    broader: reviewer_role
    specific: reviewer-pro

  llm_pro_over_general_backend:
    broader: developer_role
    specific: llm-pro

  cnn_over_general_ml:
    broader: developer_role
    specific: cnn

  researcher_pro_over_general_planning:
    broader: product_manager_role
    specific: researcher-pro
```

---

## Required agent behavior

Before implementation, testing, or review, the agent should state internally which skills apply.

When producing output for larger tasks, include a short note if useful:

```md
## Skills Applied
- python-pro
- fastapi
```

For small tasks, this can be omitted unless it helps the human understand the validation or implementation approach.
