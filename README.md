# AgentCrew

AgentCrew is a Markdown-first workflow for coordinating AI coding agents like a small software team.

It gives agents roles, playbooks, skills, handoff formats, review rules, and human approval gates.

AgentCrew lives outside your project repositories. Register it once where your agent supports global instructions, or use a tiny adapter that points to the external checkout.

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

AgentCrew uses staged loading: agents route first, then load only the role, lane, Skills, gates, and templates needed for the task. Normal user requests are routed automatically; users do not need to name roles or lanes.

## Quick Start

Clone AgentCrew once outside your projects:

```bash
git clone https://github.com/mlguyYT/AgentCrew.git ~/AgentCrew
~/AgentCrew/bin/agentcrew install
~/AgentCrew/bin/agentcrew doctor
```

From any project, ask normally:

```text
Fix the login form so empty email shows a validation message.
```

AgentCrew is registered globally for supported agents, reads its own instructions, chooses the lane, role, and Skills, and stops where human approval is required. Cursor, GitHub Copilot, and other tools can use the adapter snippets in `agent-team/adapters/` when they need a tool-specific instruction surface.

Optional: make the current task visible with `~/AgentCrew/bin/agentcrew start --task "your request"`.

Optional: create a testable task brief with `~/AgentCrew/bin/agentcrew brief --task "your request"`.

Optional: create a PR-sized work plan with `~/AgentCrew/bin/agentcrew plan --task "your request"`.

Optional: check implementation readiness with `~/AgentCrew/bin/agentcrew ready`.

No AgentCrew files need to be copied into the project.

## Workflows

Fast Lane is for small, reversible work:

```text
Developer -> Tester -> Reviewer/PM when needed -> Human
```

Full Lane is for risky or ambiguous work:

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Human
```

Specialist reviewers and agents are used only when needed: Security, UX / Design, Documentation, LLM, Researcher, CNN, and Skill Validator.

Quality profiles tune how much rigor AgentCrew applies: Light for prototypes and tiny work, Standard by default, Strict for high-impact teams, and Regulated for compliance-heavy work.

Workflow recipes give common requests a practical handling pattern, such as bug fix, feature, refactor, docs update, review, validation, research, release, incident, or Skill change.

## What Is Included

```text
AGENTS.md              entry point for agents
bin/                   registration, diagnostics, and project detection commands
agent-team/            roles, playbooks, skills, templates, policies
docs/                  install, usage, examples, customization
examples/              example prompts and workflows
.github/               optional issue and PR templates
runtime/               optional future orchestration notes
```

## Useful Docs

- [Installation](docs/installation.md)
- [Setup Doctor](docs/doctor.md)
- [Project Detection](docs/project-detection.md)
- [Task Classifier](docs/task-classifier.md)
- [Task Intake](docs/task-intake.md)
- [Acceptance Criteria](docs/acceptance-criteria.md)
- [Work Planning](docs/work-planning.md)
- [Implementation Readiness](docs/implementation-readiness.md)
- [Status Dashboard](docs/status-dashboard.md)
- [Human Decision Queue](docs/human-decision-queue.md)
- [Quality Profiles](docs/quality-profiles.md)
- [Workflow Recipes](docs/workflow-recipes.md)
- [Automatic Loading](docs/auto-load.md)
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
- store personal/local setup in shared project state

Human approval stays final.

## Session Saving

To save local pause/resume context in a target project:

```bash
~/AgentCrew/agent-team/tools/save-session.sh --project . --title "short title"
```

This writes a safe checkpoint under `.agent-state/sessions/`.
Each project gets its own `.agent-state/` folder, so session memory does not mix across projects.

To list saved sessions or show the latest one:

```bash
~/AgentCrew/agent-team/tools/list-sessions.sh --project .
~/AgentCrew/agent-team/tools/list-sessions.sh --project . --latest
```

## Status

AgentCrew is a lightweight methodology package. The core workflow is usable now. The `runtime/` folder is optional design material for future orchestration.

## License

MIT
