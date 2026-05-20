# Folder Structure

Recommended structure:

```text
agent-team/
  README.md
  STRUCTURE.md

  adapters/
    README.md
    claude-code.md
    codex.md
    openclaw.md
    cursor.md
    copilot.md

  context/
    route-index.md
    fast-lane-context.md
    full-lane-context.md
    review-context.md
    research-context.md

  agents/
    advisor.md
    idea-consultant.md
    product-manager.md
    developer.md
    tester.md
    reviewer.md
    security-reviewer.md
    ux-design-reviewer.md
    documentation-agent.md
    llm-agent.md
    researcher-agent.md
    cnn-agent.md
    skill-validator.md

  playbooks/
    fast-lane.md
    full-lane.md
    pr-process.md
    rework-loop.md
    task-classification.md
    request-routing.md
    lane-escalation.md
    specialist-review-routing.md
    default-branch-merge.md
    dependency-supply-chain.md
    behavior-preserving-refactor.md
    compatibility-rollout.md
    token-safe-mode.md
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
    state-artifacts.md
    token-discipline.md

  conventions/
    naming.md

  tools/
    detect-project.sh
    list-sessions.sh
    save-session.sh

  templates/
    idea-brief.md
    product-plan.md
    task.md
    task-routing.md
    pr-description.md
    test-report.md
    review-report.md
    security-review-report.md
    ux-design-review-report.md
    documentation-report.md
    compact-handoff.md
    compact-test-report.md
    compact-review-report.md
    compact-research-report.md
    llm-report.md
    research-report.md
    cnn-report.md
    memory-summary.md
    skill-validation-report.md

  skills/
    README.md
    registry.md
    authoring-guide.md
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
      llm-pro.md
      researcher-pro.md
    ml/
      cnn.md

  policies/
    human-in-the-loop.md
    no-autonomous-merge.md
    scope-control.md
    secrets-policy.md

  checklists/
    agentcrew-health-check.md
    definition-of-done.md
    testing.md
    code-review.md
    design-review.md
    documentation.md
    llm-review.md
    research-quality.md
    cnn-review.md
    human-approval.md
    release-readiness.md
    security.md
    memory-saving.md
    skill-validation.md
    shared-memory-refresh.md
    integration-test-escalation.md
```

AgentCrew repository structure:

```text
AGENTS.md
bin/
  agentcrew
agent-team/
docs/
examples/
.github/
```

Target projects do not need this structure unless intentionally vendoring AgentCrew.

Recommended project-state artifact structure:

```text
.agent-state/
  sessions/
  current-task.md
  decisions.md
  handoff.md
  test-report.md
  review-report.md
  security-review-report.md
  ux-design-review-report.md
  documentation-report.md
  memory.md
```

`.agent-state/` is for project-specific handoff artifacts. It is not part of the reusable AgentCrew package.
See `agent-team/protocols/state-artifacts.md`.

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

See `agent-team/conventions/naming.md`.

---

## Tool-specific adapters

Tool-specific adapters live in:

```text
agent-team/adapters/
```

The preferred setup is the one-time installer:

```bash
~/AgentCrew/bin/agentcrew install
```

This writes small global loaders for supported tools. Project-local adapters are optional fallbacks and should reference the external AgentCrew paths instead of duplicating content:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
```

---

## Optional runtime structure

Runtime and orchestration material is optional and should live outside the reusable core:

```text
runtime/
  README.md
  agents/
  coordinator/
  integrations/
  playbooks/
```

Keep optional orchestration, GitHub App, container, and worker design in `runtime/`.
