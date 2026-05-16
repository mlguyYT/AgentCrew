# AgentCrew

AgentCrew is a Markdown-first workflow for coordinating AI coding agents like a small software team.

It gives agents roles, playbooks, skills, handoff formats, review rules, and human approval gates.

AgentCrew lives outside your project repositories. You load it from Codex, Claude Code, Cursor, GitHub Copilot, or any coding agent that can read local files.

It is not a runtime, server, bot, or CI/CD platform by default.

## Why

Most agent workflows fail in the same places: unclear ownership, giant changes, weak testing, missing review, and agents treating approval as their job.

AgentCrew keeps the useful parts simple:

- roles define responsibility
- playbooks define process
- skills define technical guidance
- templates define output shape
- policies keep human approval final

AgentCrew lets agents do the work, testing, review, and preparation, but keeps final product direction, risk acceptance, PR approval, and merging with the human.

## Quick Start

Clone AgentCrew once outside your projects:

```bash
git clone https://github.com/mlguyYT/AgentCrew.git ~/AgentCrew
```

From any project, tell your coding agent:

```text
Load AgentCrew from ~/AgentCrew.
Use Fast Lane by default.
Do not merge pull requests.
Keep PRs small.
```

For fuller guidance, use:

```text
Load AgentCrew from ~/AgentCrew.

Read ~/AgentCrew/AGENTS.md and ~/AgentCrew/agent-team/.

Use Fast Lane by default.
Use Full Lane for risky work.
Do not merge pull requests.
Keep PRs small.
Route implementation rework back to the Developer.
Load relevant Skills from ~/AgentCrew/agent-team/skills/registry.md.
Keep handoffs compact using ~/AgentCrew/agent-team/protocols/communication.md.
```

No AgentCrew files need to be copied into the project.

## Workflows

Fast Lane is for small, reversible work:

```text
Developer -> Tester -> Human
```

Full Lane is for risky or ambiguous work:

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Human
```

Specialist reviewers are used only when needed: Security, UX / Design, Documentation, and Skill Validator.

## What Is Included

```text
AGENTS.md              entry point for agents
agent-team/            roles, playbooks, skills, templates, policies
docs/                  install, usage, examples, customization
examples/              example prompts and workflows
.github/               optional issue and PR templates
runtime/               optional future orchestration notes
```

## Useful Docs

- [Installation](docs/installation.md)
- [Use in an Existing Project](docs/bootstrap-existing-project.md)
- [Usage Guide](docs/usage.md)
- [Examples](docs/examples.md)
- [Customization](docs/customization.md)
- [Security](docs/security.md)
- [Contributing](docs/contributing.md)

## Rules That Matter

Agents must not:

- merge pull requests
- approve as the human
- bypass branch protection
- commit secrets
- hide failing tests
- make unrelated changes

Human approval stays final.

## Status

AgentCrew is a lightweight methodology package. The core workflow is usable now. The `runtime/` folder is optional design material for future orchestration.

## License

MIT
