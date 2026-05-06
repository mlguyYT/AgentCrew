# Full Lane Playbook

## Purpose

Full Lane is the high-quality workflow for risky or important work.

It adds more structure and review before implementation.

---

# 1. Use Full Lane For

```yaml
use_for:
  - auth
  - billing
  - security
  - infrastructure
  - CI/CD
  - Kubernetes
  - database migrations
  - public APIs
  - large refactors
  - production-critical paths
```

---

# 2. Full Lane Flow

```text
Human idea
  -> Advisor Agent
  -> Idea Consultant Agent
  -> Human concept approval
  -> Product Manager Agent
  -> Human backlog approval
  -> Developer Agent
  -> Tester Agent
  -> Reviewer Agent
  -> Human PR approval
  -> Human merge
```

---

# 3. Full Lane Rules

```yaml
rules:
  advisor_required: true
  idea_consultant_required: true
  product_manager_required: true
  tester_required: true
  reviewer_required: true
  human_concept_approval_required: true
  human_backlog_approval_required: true
  human_pr_approval_required: true
  agents_may_merge: false
```

---

# 4. Full Lane Quality Requirements

```yaml
quality_requirements:
  - acceptance criteria must be explicit
  - tests must be documented
  - risks must be documented
  - reviewer report required
  - CI failures must be resolved
  - human must approve final PR
```

---

# 5. Full Lane Exit Criteria

The PR can reach human review only when:

```yaml
ready_for_human_review:
  - tests passed or limitations documented
  - reviewer has no high/critical findings
  - acceptance criteria are satisfied
  - risk is visible
```
