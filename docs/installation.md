# Installation Guide

## Purpose

This guide explains how to install AgentCrew once and make it available to coding agents across projects.

AgentCrew is Markdown-first and tool-agnostic.
It is not a runtime, server, bot, or CI/CD platform by default.

---

## Quick Install

Place AgentCrew once outside your project repositories:

```text
~/AgentCrew/
```

Example:

```bash
git clone https://github.com/mlguyYT/AgentCrew.git ~/AgentCrew
~/AgentCrew/bin/agentcrew install
~/AgentCrew/bin/agentcrew doctor
~/AgentCrew/bin/agentcrew status
```

Do not copy `AGENTS.md` or `agent-team/` into each project by default.

From the target project, ask normally and enjoy development with your AgentCrew.

Optional: inspect a target project profile and classify a request without changing the project:

```bash
~/AgentCrew/bin/agentcrew detect-project --project /path/to/your-project
~/AgentCrew/bin/agentcrew preset --dry-run --project /path/to/your-project
~/AgentCrew/bin/agentcrew classify --project /path/to/your-project --task "Add OAuth login"
~/AgentCrew/bin/agentcrew start --dry-run --project /path/to/your-project --task "Add OAuth login"
~/AgentCrew/bin/agentcrew brief --dry-run --project /path/to/your-project --task "Add OAuth login"
~/AgentCrew/bin/agentcrew plan --dry-run --project /path/to/your-project --task "Add OAuth login"
~/AgentCrew/bin/agentcrew ready --dry-run --project /path/to/your-project
~/AgentCrew/bin/agentcrew pr-pack --dry-run --project /path/to/your-project
~/AgentCrew/bin/agentcrew status --project /path/to/your-project
```

For an existing repository, follow:

```text
docs/bootstrap-existing-project.md
```

---

## Loading model

AgentCrew uses staged loading to reduce token usage. Supported agents should read `AGENTS.md`, then `agent-team/context/route-index.md`, then only the context profile, role, Skills, gates, and templates triggered by the task.

---

## First command to give your coding agent

From the target project, ask your coding agent:

```text
Fix the login form so empty email shows a validation message.
```

AgentCrew should read its own instructions, classify the task, choose the lane, role, and Skills, and stop where human approval is required.

For automatic-loading details, read:

```text
docs/auto-load.md
```

---

## Verify external installation

Run the setup doctor:

```bash
~/AgentCrew/bin/agentcrew doctor
```

A healthy setup reports zero failures. Warnings are useful context, such as a missing optional tool loader or a loader that points to a different checkout.

See `docs/doctor.md` for details.

---

## Recommended local structure

After installation, AgentCrew should live outside the project it is guiding:

```text
~/AgentCrew/
  AGENTS.md
  bin/
    agentcrew
  docs/
  examples/

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
      security-reviewer.md
      ux-design-reviewer.md
      documentation-agent.md
      release-manager.md
      skill-validator.md

    playbooks/
      fast-lane.md
      full-lane.md
      pr-process.md
      rework-loop.md
      task-classification.md
      request-routing.md
      task-intake.md
      project-presets.md
      acceptance-criteria.md
      work-planning.md
      implementation-readiness.md
      pr-preparation.md
      release-management.md
      quality-profile-selection.md
      human-decision-queue.md
      lane-escalation.md
      specialist-review-routing.md
      skill-loading.md
      skill-validation.md
      memory-saving.md

    presets/
      README.md
      react-frontend.md
      python-api.md
      node-service.md
      general-library.md
      cli-tool.md

    quality-profiles/
      light.md
      standard.md
      strict.md
      regulated.md

    recipes/
      README.md
      bug-fix.md
      feature.md
      refactor.md
      docs-update.md
      review.md
      validation.md
      research.md
      release.md
      incident.md
      skill-change.md

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
      classify-task.sh
      select-preset.sh
      start-task.sh
      brief-task.sh
      plan-task.sh
      ready-check.sh
      prepare-pr-pack.sh
      detect-project.sh
      project-status.sh
      list-sessions.sh
      save-session.sh

    templates/
      idea-brief.md
      product-plan.md
      task.md
      task-routing.md
      current-task.md
      project-preset.md
      task-brief.md
      work-plan.md
      readiness-report.md
      pr-pack.md
      human-decision-queue.md
      pr-description.md
      test-report.md
      review-report.md
      security-review-report.md
      ux-design-review-report.md
      documentation-report.md
      release-report.md
      memory-summary.md
      skill-validation-report.md

    skills/
      README.md
      registry.md
      authoring-guide.md
      languages/
      frameworks/
      frontend/
      platform/
      professional/

    checklists/
      agentcrew-health-check.md
      definition-of-done.md
      testing.md
      code-review.md
      design-review.md
      documentation.md
      security.md
      memory-saving.md
      skill-validation.md

/path/to/your-project/
  application files
  project docs
  project tests
```

---

## Automatic loading and optional tool adapters

The preferred setup is:

```bash
~/AgentCrew/bin/agentcrew install
```

This writes small global loaders for supported tools and keeps AgentCrew outside target repositories.

Supported automatic registrations currently include Claude Code, Codex, and OpenClaw. The default installer registers OpenClaw when OpenClaw is detected; use `--agent openclaw` to force OpenClaw registration explicitly.

Tool adapter guidance lives in:

```text
agent-team/adapters/
```

If you choose to add a tiny project-local adapter as a fallback, it should point to the external AgentCrew path:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
```

Do not duplicate or vendor the whole system into every project.

---

## Minimal Load Fallback

Use this only when an agent does not honor global registration and you do not want to add a project-local adapter.

For a very small task, ask the agent to read only:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
  agents/
    product-manager.md
    developer.md
    tester.md
    reviewer.md
  playbooks/
    fast-lane.md
    pr-process.md
    rework-loop.md
    memory-saving.md
  templates/
    task.md
    product-plan.md
    pr-description.md
    test-report.md
    review-report.md
    memory-summary.md
  skills/
    registry.md
```

This supports:

```text
Developer -> Tester -> Reviewer when risk is meaningful -> Product Manager when scope or product behavior changes -> Human
```

Load specialist reviewer files and templates when the project touches security, UX, documentation, or Skill changes.

---

## Full Load Fallback

Use this only when an agent does not honor global registration.

For product and planning support, ask the agent to read the full external AgentCrew folder.

This supports:

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human
```

## Next step

Read:

```text
docs/usage.md
```
