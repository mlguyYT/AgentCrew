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
```

Do not copy `AGENTS.md` or `agent-team/` into each project by default.

From the target project, ask normally and enjoy development with your AgentCrew.

Optional: inspect a target project profile without changing it:

```bash
~/AgentCrew/bin/agentcrew detect-project --project /path/to/your-project
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
