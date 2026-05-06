# Installation Guide

## Purpose

This guide explains how to add the Agent Team workflow to any software project.

The workflow is Markdown-first and tool-agnostic.  
It does not require Docker, Kubernetes, or a special runtime.

---

## Quick install

Copy these into your project:

```text
AGENTS.md
agent-team/
```

Example:

```bash
cp AGENTS.md /path/to/your-project/
cp -r agent-team /path/to/your-project/
```

Then commit:

```bash
git add AGENTS.md agent-team
git commit -m "Add agent team workflow"
```

---

## Recommended project structure

After installation:

```text
your-project/
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
      frameworks/
      frontend/
      platform/
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

These files should point to:

```text
AGENTS.md
agent-team/
```

Do not duplicate the whole system in every adapter.

---

## Minimal install

For a very small project, install only:

```text
AGENTS.md
agent-team/
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
Developer -> Tester -> Reviewer -> Human
```

---

## Full install

For product and planning support, install everything.

This supports:

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Human
```

---

## First command to give your coding agent

After installation, ask your coding agent:

```text
Read AGENTS.md and the agent-team folder.

Use Fast Lane by default.
For risky work, use Full Lane.
Do not merge code.
Keep PRs small.
Route rework back to the Developer.
```

---

## Verify installation

Check that these files exist:

```bash
test -f AGENTS.md
test -d agent-team
test -f agent-team/playbooks/fast-lane.md
test -f agent-team/agents/developer.md
test -f agent-team/skills/registry.md
test -f agent-team/playbooks/memory-saving.md
test -f agent-team/playbooks/skill-validation.md
test -f agent-team/protocols/communication.md
test -f agent-team/templates/pr-description.md
```

---

## Next step

Read:

```text
docs/usage.md
```
