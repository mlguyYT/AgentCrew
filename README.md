# AgentCrew

AgentCrew is a Markdown-first workflow for coordinating AI coding agent teams with roles, playbooks, skills, handoffs, and human approval gates.

It is designed to live outside your project repositories and be loaded by tools that can read local instructions, including Codex, Claude Code, Cursor, GitHub Copilot, and similar coding agents.

AgentCrew is not a runtime, server, bot, or CI/CD platform by default.
It is a lightweight instruction system that helps AI agents work like a disciplined software team.

---

## For Coding Agents

Read `/path/to/AgentCrew/AGENTS.md` first.

Then read the relevant role, playbook, Skills, and templates under `/path/to/AgentCrew/agent-team/`.

Use Fast Lane by default.

Do not merge pull requests.

---

## Core Idea

AgentCrew is built around this principle:

```text
roles define responsibility
playbooks define process
skills define technical guidance
templates define output shape
policies define safety boundaries
human approval remains final
```

Agents may prepare work, implement changes, test, review, and create pull requests.

Agents may not approve as the human or merge pull requests.

---

## What Is Included

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
- skills add technology-specific execution guidance
- communication protocols keep handoffs compact
- memory saving preserves handoff context safely
- skill validation keeps skills useful and safe

---

## Core Vs Optional

Inside the external AgentCrew checkout:

Core:

```text
/path/to/AgentCrew/AGENTS.md
/path/to/AgentCrew/agent-team/
```

Optional but useful:

```text
/path/to/AgentCrew/docs/
/path/to/AgentCrew/examples/
/path/to/AgentCrew/.github/
/path/to/AgentCrew/runtime/
```

The `runtime/` folder is optional design material for future orchestration. The core AgentCrew workflow does not require any runtime, container platform, or custom service.

---

## Default Workflow

Use Fast Lane for most small work:

```text
Task
  -> Developer
  -> Tester
  -> Reviewer only if needed
  -> Human approval
```

Use Full Lane for risky work:

```text
Idea
  -> Advisor
  -> Idea Consultant
  -> Product Manager
  -> Human concept approval
  -> Product Manager backlog planning
  -> Human backlog approval
  -> Developer
  -> Tester
  -> Reviewer
  -> Specialist Reviewer if needed
  -> Human PR approval
```

Use Fast Lane for low-risk work such as docs, small fixes, simple tests, isolated features, and low-risk refactors.

Use Full Lane for auth, billing, customer data, migrations, infrastructure, CI/CD, public APIs, large refactors, or high-impact product changes.

---

## Human Approval Stays Final

AgentCrew lets agents do the work, testing, review, and preparation, but keeps final product direction, risk acceptance, PR approval, and merging with the human.

Agents must not:

- merge pull requests
- approve as the human
- bypass branch protection
- commit secrets
- hide failing tests
- make unrelated changes

---

## Quick Install

Clone or place AgentCrew once outside your project repositories:

```bash
git clone git@github.com-mlguyyt:mlguyYT/AgentCrew.git ~/AgentCrew
```

Then, from any project, tell your coding agent to load AgentCrew from that external path.

No AgentCrew files need to be copied into the project.

Optional: if you want GitHub issue or PR templates in a project, copy only the `.github/` templates:

```bash
cp -r .github /path/to/your-project/
```

---

## First Prompt To Your Coding Agent

From your project repository, tell your coding agent:

```text
Load AgentCrew from ~/AgentCrew.

Read ~/AgentCrew/AGENTS.md and ~/AgentCrew/agent-team/.

Use Fast Lane by default.
Use Full Lane for risky work.
Do not merge pull requests.
Keep PRs small.
Route implementation rework back to the Developer.
Load relevant Skills automatically from ~/AgentCrew/agent-team/skills/registry.md.
Keep handoffs compact using ~/AgentCrew/agent-team/protocols/communication.md.
```

---

## Roles

AgentCrew defines role files under:

```text
~/AgentCrew/agent-team/agents/
```

Core roles:

- Advisor: evaluates idea direction and risk
- Idea Consultant: turns a rough idea into a structured brief
- Product Manager: creates scope, tasks, acceptance criteria, and priorities
- Developer: implements focused changes
- Tester: validates behavior and acceptance criteria
- Reviewer: checks correctness, scope, maintainability, risk, and tests

Specialist roles may include:

- Security Reviewer: checks auth, secrets, data, dependencies, and infrastructure risk
- UX / Design Reviewer: checks usability, accessibility, responsive behavior, and visual quality
- Documentation Agent: updates and reviews docs, examples, changelog, and release notes
- Skill Validator: reviews skills when they are added or changed

---

## Skills

Skills are technology and professional-practice profiles that agents load when a task touches a language, framework, frontend stack, platform, or role-specific practice.

Examples:

```text
FastAPI task      -> python-pro + fastapi
React component   -> typescript-pro + react
Kubernetes YAML   -> kubernetes
PR review         -> reviewer-pro
Backlog work      -> product-owner-pro
```

Current skills may include:

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

See:

```text
agent-team/skills/registry.md
```

Use the Skill Validator when adding or changing skills:

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
```

---

## Communication Protocol

AgentCrew prefers compact artifacts over long chat.

Default handoff format:

```md
### Context
1-3 bullets only.

### Decision
What was decided.

### Evidence
Only facts needed by the next agent.

### Next Action
Exactly what the next agent should do.

### Open Questions
Only blockers.
```

Core protocol files:

```text
agent-team/protocols/communication.md
agent-team/protocols/handoff-format.md
agent-team/protocols/token-discipline.md
agent-team/protocols/state-artifacts.md
```

---

## Project State

Project-specific handoff artifacts should live in:

```text
.agent-state/
```

The `agent-team/` folder contains reusable methodology.

The `.agent-state/` folder contains current project state.

Example:

```text
.agent-state/
  current-task.md
  decisions.md
  handoff.md
  test-report.md
  review-report.md
  memory.md
```

Do not store secrets, tokens, raw customer data, or large logs in `.agent-state/`.

---

## Memory Saving

Use the memory-saving playbook when work pauses, a meaningful decision is made, or another agent needs handoff context.

Memory can include:

- decisions
- current status
- commands run
- risks
- next steps

Memory must not include:

- secrets
- tokens
- passwords
- raw customer data
- sensitive production data
- large logs

See:

```text
agent-team/playbooks/memory-saving.md
agent-team/templates/memory-summary.md
```

---

## Optional Runtime Layer

AgentCrew can be extended later with an orchestrated runtime, coordinators, integrations, containers, and job workers.

This is optional.

The core AgentCrew workflow does not require any runtime, container platform, or custom service.

---

## Start Here

1. Read `docs/bootstrap-existing-project.md`.
2. Clone or place AgentCrew outside your target repository.
3. From the target repository, tell your coding agent to load `~/AgentCrew/AGENTS.md`.
4. Run the health check in `~/AgentCrew/agent-team/checklists/agentcrew-health-check.md`.
5. Read `docs/installation.md`.
6. Read `docs/usage.md`.
7. Read `docs/examples.md`.
8. Ask your coding agent to follow Fast Lane by default.

---

## Recommended First Workflow

Start with:

```text
Product Manager
  -> Developer
  -> Tester
  -> Reviewer
  -> Human
```

For small tasks, use:

```text
Developer
  -> Tester
  -> Human
```

Once that works, add Advisor, Idea Consultant, specialist reviewers, and skills as needed.

---

## License

MIT
