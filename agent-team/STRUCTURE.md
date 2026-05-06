# Folder Structure

Recommended structure:

```text
agent-team/
  README.md
  STRUCTURE.md

  agents/
    advisor.md
    idea-consultant.md
    product-manager.md
    developer.md
    tester.md
    reviewer.md
    skill-validator.md

  playbooks/
    fast-lane.md
    full-lane.md
    pr-process.md
    rework-loop.md
    task-classification.md
    skill-loading.md
    skill-validation.md
    memory-saving.md

  workflows/
    idea-to-task.md
    task-to-pr.md
    pr-review.md
    rework.md

  protocols/
    communication.md
    handoff-format.md
    token-discipline.md

  templates/
    idea-brief.md
    product-plan.md
    task.md
    pr-description.md
    test-report.md
    review-report.md
    memory-summary.md
    skill-validation-report.md

  skills/
    README.md
    registry.md
    languages/
      python-pro.md
      typescript-pro.md
      javascript-pro.md
      sql-pro.md
      java-pro.md
      csharp-pro.md
      cpp-pro.md
      go-pro.md
      rust-pro.md
      php-pro.md
      shell-pro.md
    frameworks/
      fastapi.md
    frontend/
      react.md
    platform/
      kubernetes.md
    professional/
      reviewer-pro.md
      product-owner-pro.md

  policies/
    human-in-the-loop.md
    no-autonomous-merge.md
    scope-control.md
    secrets-policy.md

  checklists/
    definition-of-done.md
    testing.md
    code-review.md
    security.md
    memory-saving.md
    skill-validation.md
```

Recommended repository-level structure:

```text
AGENTS.md
agent-team/
docs/
examples/
.github/
```

Recommended project-state artifact structure:

```text
.agent-state/
  current-task.md
  idea-brief.md
  product-plan.md
  test-report.md
  review-report.md
  decisions.md
```

`.agent-state/` is for project-specific handoff artifacts. It is not part of the reusable Agent Team package.

---

## Naming convention

Use kebab-case for files:

```text
product-manager.md
idea-consultant.md
pr-process.md
task-classification.md
```

Use clear headings inside every file.

---

## Tool-specific adapters

Optional adapters can be added later:

```text
.codex/AGENTS.md
.github/copilot-instructions.md
.cursor/rules/agent-team.md
.claude/CLAUDE.md
```

These should reference the canonical `agent-team/` folder instead of duplicating content.

---

## Optional runtime structure

Runtime and orchestration material is optional and should live outside the copyable core:

```text
runtime/
  README.md
  agents/
  coordinator/
  integrations/
  playbooks/
```

Keep Docker, Kubernetes, OpenClaw, GitHub App, and worker orchestration design in `runtime/`.
