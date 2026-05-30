# AgentCrew

**Turn your coding agent into a disciplined team.**

AgentCrew is a Markdown-first methodology for agentic coding. Your existing coding agent — Claude Code, Codex, Cursor, OpenClaw, Hermes, or another compatible assistant — loads it as guidance and uses it to work through software tasks with roles, routing, handoffs, quality gates, and human approval.

You do not change how you work. You keep talking to your agent. AgentCrew gives that chat a team process underneath.

AgentCrew is not a runtime.  
It is not a daemon.  
It is not a replacement for CI.  
It is a practical operating system for coding agents, written mostly in Markdown and shell.

---

## The problem

A single coding-agent session is usually one context doing every job: scoping, implementing, testing, reviewing, documenting, and sometimes pretending it can approve the work it just wrote.

That is not how good software teams work.

The same model that wrote the bug should not be the only reviewer of the bug. The same chat that guessed an API should not be the final authority that the API is correct. A risky authentication change should not be treated like a typo fix. A refactor should not silently expand across unrelated parts of the codebase.

Most teams try to fix this with bigger prompts or “be careful” notes in `CLAUDE.md`, `AGENTS.md`, or editor rules. That helps a little, but the agent can still tunnel-vision, skip tests, lose context, make unrelated edits, or leave humans with a giant diff that is hard to trust.

AgentCrew exists to give coding agents a process before they touch the code.

---

## Why we built this

We built AgentCrew after repeatedly running into the same problem with coding agents: they can write code fast, but they do not naturally follow a disciplined development cycle.

Every serious change needs more than implementation. The agent should understand the task, pick the right context, use the right skills, write or update tests, verify that those tests actually work, document the change, and prepare something a human can review.

Without that structure, we found ourselves repeating the same instructions again and again:

- write the tests;
- run the tests;
- check the edge cases;
- document what changed;
- do not merge;
- do not make unrelated edits;
- do not skip the review.

The failure mode is not theoretical. We have seen agent-assisted refactors create messy changes across a codebase, miss important context, and leave humans with days of cleanup. In one case, a refactor that should have been controlled ended up breaking enough pieces that fixing it manually took about a week. The problem was not that the model was useless. The problem was that it had no real process, no specialized role, no skill boundary, and no serious review gate.

We tried bigger prompts, project rules, internal Codex workflows, prompt stacks, and command-based approaches. Some helped. But they still required too much manual steering, especially when we wanted the agent itself to recognize when a task needed planning, testing, review, security attention, or a human decision.

AgentCrew is the system we wanted: not a magical autopilot, and not a replacement for developer judgment. It is a disciplined methodology for agentic coding — roles, skills, routing, handoffs, quality gates, memory, and approval boundaries — so coding agents become easier to trust, easier to review, and more useful in real development work.

---

## What you actually experience

You ask your normal coding agent for an outcome:

> Add Google OAuth login to the signup page.

With AgentCrew loaded, the agent does not jump straight into editing files. It first follows the methodology:

1. **Classify the request**  
   A pure-bash classifier can identify the task type, risk level, lane, likely role, relevant skills, and quality gates.

2. **Pick the right lane**  
   Simple, low-risk work can use a fast lane. Risky, multi-step, security-sensitive, or architecture-changing work uses a fuller workflow.

3. **Start with the right role**  
   The agent may begin as an Advisor or Product Manager to clarify scope and acceptance criteria before implementation.

4. **Implement as Developer**  
   The Developer role focuses on minimal, relevant changes. It must avoid unrelated edits, hidden failures, unsafe commands, and premature merge decisions.

5. **Check as Tester**  
   The Tester role focuses on verification. It should run or propose the right tests and report what passed, failed, or could not be checked.

6. **Review as Reviewer or Security Reviewer**  
   Risky code paths, authentication, authorization, payments, migrations, secrets, and infrastructure changes get stricter review guidance.

7. **Produce a handoff**  
   The final output is not just “done.” It should include what changed, what was tested, what risks remain, and what needs human approval.

8. **Stop at the human gate**  
   AgentCrew does not treat the agent as the final approver. A human still decides what lands.

You stay in your normal agent chat. AgentCrew gives that chat a routing system, role instructions, handoff formats, state artifacts, and approval gates, so the work follows a team process instead of one long unstructured session.

---

## Install

Clone AgentCrew somewhere outside your project:

```bash
git clone https://github.com/mlguyYT/AgentCrew ~/AgentCrew
```

Register AgentCrew with your host agent:

```bash
~/AgentCrew/bin/agentcrew install
```

Verify the setup:

```bash
~/AgentCrew/bin/agentcrew doctor
```

Then open your normal coding agent and start working as usual.

AgentCrew installs a small loader block into your host-agent instruction file, such as:

```text
~/.claude/CLAUDE.md
~/.codex/AGENTS.md
~/.hermes/SOUL.md
```

The loader points the host agent to the AgentCrew methodology. Your project does not need a new runtime dependency.

---

## What is in the box

```text
agent-team/
├─ agents/              Role definitions such as Advisor, PM, Developer,
│                       Tester, Reviewer, Security Reviewer, UX Reviewer,
│                       Documentation Agent, and more
│
├─ tools/               CLI helpers, including the pure-bash task classifier
│
├─ playbooks/           How to route tasks, handle gates, prepare PRs,
│                       manage rework, and save useful memory
│
├─ recipes/             Workflow recipes for features, bug fixes, refactors,
│                       migrations, reviews, security-sensitive work, and more
│
├─ protocols/           Handoff format, state artifacts, approval boundaries,
│                       and token-discipline rules
│
├─ context/             Route index and lane-specific context profiles
│
├─ checklists/          Pre-merge readiness, review checks, memory refreshes,
│                       and other quality controls
│
├─ templates/           Task briefs, work plans, compact handoffs, review
│                       reports, PR descriptions, and session summaries
│
└─ skills/              Technical and professional skills that can be loaded
                        only when relevant

bin/agentcrew           install, doctor, status, classify, context, start,
                        brief, plan, ready, pr-pack, checkpoint, save-session,
                        restore-session, detect-project, preset
```

The methodology is Markdown.  
The classifier and setup helpers are shell scripts.  
There is no daemon and no required runtime inside your project.

---

## Fast Lane vs Full Lane

Not every task needs a heavy workflow.

AgentCrew separates work into lanes so the agent does not over-process simple tasks or under-process risky ones.

### Fast Lane

Used for small, low-risk work:

- typo fixes;
- small documentation updates;
- simple tests;
- minor localized changes;
- straightforward explanations;
- low-risk cleanup.

The goal is speed with basic discipline.

### Full Lane

Used for work that needs stronger control:

- authentication or authorization changes;
- payment logic;
- database migrations;
- security-sensitive code;
- infrastructure changes;
- large refactors;
- production-risky behavior;
- unclear requirements;
- multi-file or multi-phase implementation.

The goal is safer execution, clearer handoffs, and better review.

---

## Roles

AgentCrew gives your coding agent role-specific instructions instead of asking one generic chat to do everything.

Common roles include:

- **Advisor** — explains, guides, and helps reason before implementation.
- **Product Manager** — clarifies scope, user value, acceptance criteria, and tradeoffs.
- **Developer** — implements focused changes with minimal unrelated edits.
- **Tester** — verifies behavior and reports what was tested.
- **Reviewer** — reviews the implementation for correctness, maintainability, and risk.
- **Security Reviewer** — checks sensitive paths such as auth, permissions, secrets, and unsafe operations.
- **UX Reviewer** — reviews user-facing behavior and interaction quality.
- **Documentation Agent** — updates or reviews documentation, examples, and usage notes.
- **Release Manager** — helps prepare release notes, readiness checks, and release handoffs.

The point is not to pretend there are separate humans. The point is to make the agent use different constraints for different phases of work.

---

## Project-local discipline

AgentCrew can keep project-local working state in `.agent-state/`.

That state may include:

```text
.agent-state/
├─ current-task.md
├─ work-plan.md
├─ human-decisions.md
├─ handoff.md
├─ test-report.md
├─ review-report.md
├─ pr-pack.md
└─ session-checkpoints/
```

This gives the agent a controlled memory surface for the current project.

The goal is not to store everything. The goal is to preserve the important parts:

- what the task is;
- what decisions were already made;
- what is in scope;
- what is out of scope;
- what changed;
- what was tested;
- what still needs human approval.

Good agent memory should be compressive, not archival.

---

## Project presets

AgentCrew can detect or configure project presets so the methodology fits the stack.

Examples:

- Python web service;
- TypeScript frontend;
- Rust CLI;
- machine-learning pipeline;
- documentation-heavy project;
- infrastructure repository;
- mobile project;
- monorepo.

A project preset can add stricter expectations, relevant skills, or extra review gates.

Project-local configuration should tighten the process. It should not remove human approval, skip required gates, or weaken core safety rules.

---

## Safety rules

AgentCrew is built around a simple principle:

> The agent can help prepare the work, but a human still owns the decision to land it.

Core rules:

- Agents must not merge their own work.
- Agents must not bypass branch protection.
- Agents must not use `git push --force` unless a human explicitly asks and the risk is understood.
- Agents must not hide failing tests.
- Agents must not claim tests passed if they were not run.
- Agents must not commit secrets.
- Agents must not make unrelated changes.
- Agents must not silently expand scope.
- Agents must not treat their own review as final approval.
- Human approval is required before landing production work.

AgentCrew cannot make an underlying model perfect. It gives the model a stricter operating process and makes failures easier to catch.

---

## What AgentCrew is not

AgentCrew is not a replacement for your judgment.

It is also not:

- a CI system;
- a deployment platform;
- a hosted service;
- a background daemon;
- a magical autonomous engineer;
- a guarantee that an AI agent will always behave correctly.

AgentCrew is a methodology and tool layer that helps coding agents behave more like disciplined collaborators.

You should still review code.  
You should still run tests.  
You should still protect your branches.  
You should still decide what gets merged.

---

## Example workflow

A typical risky feature request might look like this:

```text
User request:
Add Google OAuth login to the signup flow.

AgentCrew route:
- Lane: Full
- Risk: Security-sensitive
- Starting role: Product Manager
- Required roles: Developer, Tester, Security Reviewer
- Required outputs: work plan, test report, security review, human decision log

Expected flow:
1. Clarify acceptance criteria.
2. Identify affected files and auth boundaries.
3. Create a work plan.
4. Implement minimal changes.
5. Add or update tests.
6. Run verification.
7. Review security-sensitive behavior.
8. Prepare compact handoff.
9. Wait for human approval.
```

The agent still works in your normal development environment. AgentCrew gives it the process to follow.

---

## CLI examples

Classify a task:

```bash
~/AgentCrew/bin/agentcrew classify "Add Google OAuth login to signup"
```

Check setup:

```bash
~/AgentCrew/bin/agentcrew doctor
```

Detect a project stack:

```bash
~/AgentCrew/bin/agentcrew detect-project
```

Prepare a task brief:

```bash
~/AgentCrew/bin/agentcrew brief "Fix flaky checkout test"
```

Prepare a PR pack:

```bash
~/AgentCrew/bin/agentcrew pr-pack
```

The CLI is there to support setup, inspection, routing, and artifacts. Daily work still happens in your normal coding agent.

---

## Why Markdown-first?

AgentCrew is Markdown-first on purpose.

Markdown is easy to read, easy to edit, easy to review, and easy for coding agents to load. It keeps the methodology transparent.

Changing how the team works should not require changing a hidden orchestration engine. In AgentCrew, roles, playbooks, skills, templates, and policies are visible files.

That makes the system easier to inspect, customize, version, and improve.

---

## Current status

AgentCrew is in pre-v0.1 development.

The Markdown methodology, host-agent loader, classifier, role files, playbooks, templates, and `.agent-state/` artifact patterns are usable today. The public contract is still stabilizing.

The first tagged release will define the stable contract for:

- role names;
- classifier output;
- host-agent loader schema;
- `agent-team/` directory layout;
- `.agent-state/` artifact names;
- core CLI commands.

Runtime-style orchestration, stronger isolation, and backend execution may be developed separately, but the core AgentCrew methodology does not require them.

---

## Roadmap

Near-term priorities:

- stronger classifier tests;
- clearer golden examples;
- better setup diagnostics;
- more project presets;
- improved documentation;
- stricter artifact validation;
- end-to-end demo workflows;
- clearer security and threat-model documentation.

Longer-term ideas:

- optional runtime execution layer;
- stronger role isolation;
- budget-aware execution;
- richer project dashboards;
- deeper integration with local and hosted coding agents.

The core principle will stay the same: AgentCrew should make coding agents more disciplined without taking final control away from humans.

---

## Documentation

- [Installation](docs/installation.md)
- [Setup Doctor](docs/doctor.md)
- [Project Presets](docs/project-presets.md)
- [Quality Profiles](docs/quality-profiles.md)
- [Workflow Recipes](docs/workflow-recipes.md)
- [Security](docs/security.md)
- [Customization](docs/customization.md)
- [FAQ](docs/faq.md)
- [Roadmap](docs/roadmap.md)

---

## License

MIT.
