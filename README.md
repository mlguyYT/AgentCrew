# Agent Team

Agent Team is a Markdown-first workflow for coordinating AI coding agents in software projects.

It is designed to be copied into any repository and used by tools that can read repository instructions, including Codex, Claude Code, Cursor, GitHub Copilot, and similar agents.

## What is included

```text
AGENTS.md
agent-team/
docs/
examples/
.github/
```

The core package is intentionally lightweight:

- roles define what each agent is responsible for
- playbooks define Fast Lane and Full Lane workflows
- templates define expected outputs
- policies preserve human approval and scope control
- Skills add technology-specific execution guidance
- memory saving preserves handoff context safely
- Skill validation keeps Skills useful and safe
- communication protocols keep agent handoffs compact

## Default workflow

Use Fast Lane for most small work:

```text
Task
  -> Developer
  -> Tester
  -> Human approval
```

Use Full Lane for risky work:

```text
Idea
  -> Advisor
  -> Idea Consultant
  -> Product Manager
  -> Developer
  -> Tester
  -> Reviewer
  -> Human approval
```

Agents may prepare work, test it, review it, and create PRs. Agents may not approve as the human or merge PRs.

## Quick install

Copy the core workflow into your project:

```bash
cp AGENTS.md /path/to/your-project/
cp -r agent-team /path/to/your-project/
```

Optional adapters are provided for common tools:

```text
.codex/AGENTS.md
.claude/CLAUDE.md
.cursor/rules/agent-team.md
.github/copilot-instructions.md
```

## Skills

Skills are technology and professional practice profiles that agents load when a task touches a language, framework, frontend stack, platform, or role-specific practice.

Current Skills:

- Python Pro
- TypeScript Pro
- JavaScript Pro
- SQL Pro
- Java Pro
- C# Pro
- C++ Pro
- Go Pro
- Rust Pro
- PHP Pro
- Shell Pro
- FastAPI
- React
- Kubernetes
- Reviewer Pro
- Product Owner Pro

See `agent-team/skills/registry.md`.

Use the Skill Validator when adding or changing Skills:

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
```

## Memory saving

Use the memory-saving playbook when work pauses, a meaningful decision is made, or another agent needs handoff context:

```text
agent-team/playbooks/memory-saving.md
agent-team/templates/memory-summary.md
```

Memory should not contain secrets, raw customer data, or large logs.

## Communication protocol

Agent handoffs should use compact artifacts instead of long chat.

Core protocol files:

```text
agent-team/protocols/communication.md
agent-team/protocols/handoff-format.md
agent-team/protocols/token-discipline.md
```

Project handoff artifacts should use:

```text
.agent-state/
```

## Optional runtime layer

The `runtime/` folder contains advanced design notes for a future orchestrated agent runtime with coordinators, GitHub integration, containers, and Kubernetes jobs.

The runtime layer is optional. The core Agent Team workflow does not require Docker, Kubernetes, OpenClaw, or any custom service.

## Start here

1. Read `docs/installation.md`.
2. Read `docs/usage.md`.
3. Read `docs/memory-saving.md` and `docs/skill-validation.md` if you plan to extend the workflow.
4. Read `docs/examples.md` for prompt examples.
5. Copy `AGENTS.md` and `agent-team/` into a target repository.
6. Ask your coding agent to follow Fast Lane by default.
