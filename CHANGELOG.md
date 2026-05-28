# Changelog

## Unreleased

## v0.1.0 - 2026-05-28

First tagged release of AgentCrew. Bundles the full Markdown-first workflow,
roles, playbooks, Skills registry, adapters, and CLI tooling that have been
maturing on `main` since the initial public push.

### Added
- Initial public AgentCrew agent-team workflow
- Tool-agnostic `AGENTS.md`
- Fast Lane and Full Lane playbooks
- Agent role definitions
- Templates
- Workflow docs
- Tool adapters
- Public documentation
- Root `README.md`, `CONTRIBUTING.md`, and `SECURITY.md`
- Categorized Skills registry
- Optional runtime layer under `runtime/`
- Memory saving playbook, checklist, and template
- Skill Validator role, playbook, checklist, and report template
- Top-level `examples/` pointer directory
- Runtime playbooks boundary note
- Root contributing/security links to detailed docs
- Agent communication protocol, handoff format, and token discipline
- Ten popular Pro Skills for TypeScript, JavaScript, SQL, Java, C#, C++, Go, Rust, PHP, and Shell
- Security Reviewer, UX / Design Reviewer, and Documentation Agent roles with templates, checklists, and runtime profiles
- Operational completeness docs for bootstrapping, health checks, naming, specialist routing, lane escalation, Skill authoring, and state artifacts
- Documentation refresh aligning public docs on AgentCrew naming, Markdown-first positioning, project state, memory, and first-use prompts
- External loading model so AgentCrew lives outside target repositories and is loaded by coding agents on demand
- Onboarding UX polish for minimal prompts, external-path adapters, and AgentCrew repository structure wording
- Natural-language request routing so users can ask for outcomes while AgentCrew chooses the lane, role, and Skills
- Simplified Quick Start prompts so users load AgentCrew and ask for outcomes without restating internal rules
- Development quality gates for modular clean architecture and at least 70 percent test coverage when coverage tooling exists
- Optional `save-session.sh` utility for local AgentCrew pause/resume checkpoints under `.agent-state/sessions/`
- Automatic per-project session memory isolation using the target project's git root
- Optional `list-sessions.sh` utility for listing checkpoints or showing the latest saved session
- One-time `bin/agentcrew install` command for global AgentCrew registration with supported coding agents
- Automatic-loading docs and adapters for Claude Code, Codex, Cursor, and GitHub Copilot
- OpenClaw adapter and installer registration support
- Hermes Agent adapter and installer registration support
- Team-neutral shared state rules with session-save personal identifier and private path checks
- Conditional Fast Lane Reviewer and Product Manager routing triggers
- Default-branch merge, dependency supply-chain, behavior-preserving refactor, compatibility rollout, shared-memory refresh, and integration-test escalation guidance
- Review report output discipline for blocking issues, risks, preserved legacy issues, test gaps, product decisions, and next phase
- LLM Agent, Researcher Agent, and CNN Agent roles with templates, checklists, skills, and routing triggers
- Token-safe staged loading with route index, context profiles, compact templates, lazy specialist loading, and output budgets
- `agentcrew doctor` setup-health command and documentation for validating files, loaders, tools, and project context
- `agentcrew detect-project` read-only project profiling for stack, package managers, validation commands, coverage hints, and suggested Skills
- Request Routing playbook and compact routing template for automatic role, lane, Skill, and gate selection
- `agentcrew classify` task classifier for previewing lane, starting role, reviewers, specialists, Skill hints, gates, and files to load
- `agentcrew status` project dashboard for loader registrations, git state, `.agent-state/` artifacts, latest sessions, reports, and human attention
- Human Decision Queue playbook, template, docs, and status dashboard support for surfacing human-only decisions
- Quality profiles for Light, Standard, Strict, and Regulated product-builder modes with routing, docs, doctor, and classifier support
- Task intake playbook, current-task template, docs, and `agentcrew start` command for turning plain requests into `.agent-state/current-task.md`
- Workflow recipes for common product-builder outcomes with classifier, task intake, status, docs, and doctor support
- Acceptance criteria playbook, task brief template, checklist, docs, and `agentcrew brief` command for creating testable task briefs
- Work planning playbook, template, checklist, docs, status support, and `agentcrew plan` command for PR-sized implementation slicing
- Implementation readiness playbook, template, checklist, docs, status support, and `agentcrew ready` command for pre-implementation readiness checks
- PR preparation playbook, template, checklist, docs, status support, and `agentcrew pr-pack` command for human-review packets
- Project presets, selector command, template, checklist, docs, and status support for project-shape defaults
- Release Manager role, release management playbook, report template, docs, routing, and state support
- Support Triage Agent role, playbook, checklist, report template, docs, routing, and state support
- Standalone scenario examples for bug fix, support triage, auth risk, release preparation, LLM review, and CNN review
- Loader management docs and `agentcrew uninstall` command for safely removing managed global loader blocks
- Token-efficiency measures: phase-based context manifests, doctor word-budget warnings, compact Skill registry, and registry guidance split
- Session checkpoint blocks, restore-session tooling, and CLI checkpoint commands for token-efficient resume context
- Direct Answer Mode for advisory questions, with tighter loaders and no extra AgentCrew file loading unless action or evidence is needed

### Fixed
- Critical-risk classifier patterns now tolerate articles and common phrasings so requests like "rotate the production secret", "drop the users table", and "force-push to main" escalate to Full Lane with explicit human decision
- Risk-driven starting role, lane, and workflow stay consistent across all action-implying intents instead of only `implementation_or_bug_fix`; held specialist intents keep their entry role but append an explicit Advisor / Reviewer / human-decision escalation step
- Topic regex patterns (support, release, docs, research, llm, cnn, skill) are consolidated as named constants used by both intent and specialist branches so terms cannot drift between the two
- Doctor loader-path check now reads only the AgentCrew-managed marker block so unrelated mentions of the path elsewhere in the loader file no longer cause false positives
- Doctor token budgets now warn when a tracked file grows more than 10% between runs, using `.agent-state/doctor-budget-history.tsv` for per-checkout history

### Security
- Installer refuses to rewrite a loader file when the existing marker block does not look like an AgentCrew-managed block (first non-blank line must be `# AgentCrew`), preventing silent overwrite of user content that happens to use our marker strings (review HIGH-1)
- `HERMES_PROFILE` and `OPENCLAW_PROFILE` env values are validated against `[A-Za-z0-9_-]+` before path interpolation; invalid values fall back to the default profile directory with a clear stderr message (review MEDIUM-1, MEDIUM-2)
- Classifier and context-manifest `yaml_quote` escape embedded newlines as `\n` so untrusted task text cannot break the emitted YAML structure (review LOW-1)
- Installer writes loader files with mode `0600` and creates parent directories with `0700` when AgentCrew created them; doctor warns when an existing loader is wider than `0600` (review LOW-3)
- `restore-session --file` rejects paths outside the resolved sessions directory, closing a confused-deputy read on arbitrary files (review LOW-4)
- Writer tools (`start`, `brief`, `plan`, `ready`, `pr-pack`, `preset`, `save-session`) refuse to create `.agent-state/` under a `--project` path that is outside `$HOME` and not a git worktree (review INFO-3)
- `add_unique` helpers in classify-task, context-manifest, and select-preset validate the array-name argument against `[A-Za-z0-9_]` before `eval`, hardening the helpers against future refactors that might let user input reach them (review INFO-2)
- `docs/task-intake.md` and `docs/security.md` document that persisted task text is verbatim and that the AgentCrew checkout is the agent's policy file — treat it like CI configuration (review LOW-2, INFO-1)
