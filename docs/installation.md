# Installation Guide

## Purpose

This guide explains how to add the AgentCrew workflow to any software project.

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
```

Do not copy `AGENTS.md` or `agent-team/` into each project by default.

From the target project, ask your coding agent to load AgentCrew from the external path.

For an existing repository, follow:

```text
docs/bootstrap-existing-project.md
```

---

## First command to give your coding agent

From the target project, ask your coding agent:

```text
Load AgentCrew from ~/AgentCrew.

Fix the login form so empty email shows a validation message.
```

AgentCrew should read its own instructions, classify the task, choose the lane, role, and Skills, and stop where human approval is required.

---

## Verify external installation

Check that these files exist:

```bash
test -f ~/AgentCrew/AGENTS.md
test -d ~/AgentCrew/agent-team
test -f ~/AgentCrew/agent-team/playbooks/fast-lane.md
test -f ~/AgentCrew/agent-team/agents/developer.md
test -f ~/AgentCrew/agent-team/skills/registry.md
test -f ~/AgentCrew/agent-team/skills/authoring-guide.md
test -f ~/AgentCrew/agent-team/playbooks/memory-saving.md
test -f ~/AgentCrew/agent-team/playbooks/skill-validation.md
test -f ~/AgentCrew/agent-team/playbooks/lane-escalation.md
test -f ~/AgentCrew/agent-team/playbooks/specialist-review-routing.md
test -f ~/AgentCrew/agent-team/protocols/communication.md
test -f ~/AgentCrew/agent-team/protocols/state-artifacts.md
test -f ~/AgentCrew/agent-team/templates/pr-description.md
test -f ~/AgentCrew/agent-team/checklists/agentcrew-health-check.md
```

---

## Recommended local structure

After installation, AgentCrew should live outside the project it is guiding:

```text
~/AgentCrew/
  AGENTS.md
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

    templates/
      idea-brief.md
      product-plan.md
      task.md
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

## Optional tool adapters

You may also add tool-specific adapter files:

```text
.codex/AGENTS.md
.github/copilot-instructions.md
.cursor/rules/agent-team.md
.claude/CLAUDE.md
```

If you choose to add a tiny project-local adapter, it should point to the external AgentCrew path:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
```

Do not duplicate or vendor the whole system into every project.

---

## Minimal Load

For a very small task, ask the agent to load only:

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/
  agents/
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
    pr-description.md
    test-report.md
    review-report.md
    memory-summary.md
  skills/
    registry.md
```

This supports:

```text
Developer -> Tester -> Reviewer if needed -> Human
```

Load specialist reviewer files and templates when the project touches security, UX, documentation, or Skill changes.

---

## Full Load

For product and planning support, load the full external AgentCrew folder.

This supports:

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human
```

## Next step

Read:

```text
docs/usage.md
```
