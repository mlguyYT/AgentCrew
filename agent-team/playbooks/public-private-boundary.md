# Public Private Boundary

## Purpose

Use this playbook when work may mix public repository content with private product, customer, commercial, or strategy content.

---

## Default Classification

Keep these private unless the human explicitly approves public handling:

- customer-specific logic
- proprietary product strategy
- commercial workflow design
- private proposal, sales, or account workflows
- sensitive positioning or messaging
- generated artifacts derived from private data

Public repository work should be reusable, sanitized, and free of private product commitments.

---

## Routing

When a request touches private product value or customer-sensitive workflows:

```text
Product Manager -> Security Reviewer or Documentation Agent if needed -> Human
```

The human decides whether work belongs in:

- the public repository
- a private local note
- an ignored runtime artifact
- a separate private workspace
- a cloud resource

---

## Before Implementation

- classify planned files with `agent-team/playbooks/artifact-classification.md`
- update `.agent-state/artifact-map.md` when useful
- record public/private decisions in `.agent-state/project-constraints.md` or `.agent-state/human-decisions.md`
- do not place private product behavior in the public repository by accident

