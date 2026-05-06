# Memory Summary

## Date
2026-05-06

## Topic
Agent Team workflow repository organization and extension.

## Status
The repository is now organized as a Markdown-first Agent Team workflow with optional runtime notes separated under `runtime/`.

## Decisions
- `agent-team/` is the canonical reusable package.
- `runtime/` is optional and contains orchestration, worker, Docker/Kubernetes/OpenClaw, and GitHub integration design notes.
- Agents use compact handoff artifacts instead of long chat.
- Skills are categorized and autoloaded from `agent-team/skills/registry.md`.
- Project-specific memory and handoff state must stay outside `agent-team/`.

## Relevant Files / Areas
- `AGENTS.md`
- `agent-team/`
- `agent-team/protocols/`
- `agent-team/skills/`
- `docs/`
- `examples/`
- `runtime/`

## Commands / Validation
Read-only and structure checks were run with `find`, `ls`, `sed`, and `rg`.

Validation confirmed:
- required core role, playbook, Skill registry, and template files exist
- `examples/` exists
- `.agent-state/` is gitignored
- communication protocols are referenced by core docs and adapters
- all templates include `## Handoff`
- ten new Pro Skills exist and are registered

## Risks / Constraints
- This folder is not currently a git repository, so git diff/status validation was not available.
- Runtime playbooks intentionally duplicate some core workflow concepts, but `runtime/playbooks/README.md` marks them optional.
- Popular Skill choices were based on broad current ecosystem signals and may need periodic review.

## Open Questions
- Should the project eventually include a CLI installer or package generator?
- Should examples grow from `docs/examples.md` into standalone files under `examples/`?
- Should more framework Skills be added for Node/Express, Django, Spring, .NET, Laravel, and Vue?

## Next Steps
- Validate the repository from a fresh clone once it becomes a git repo.
- Consider adding a release checklist for publishing the first public version.
- Consider adding example `.agent-state/` artifacts as documentation-only samples.

## Notes
No secrets, raw logs, customer data, or sensitive production data were included.

## Handoff

### Context
- Core workflow lives in `agent-team/`; optional runtime lives in `runtime/`.
- Skills, memory saving, Skill validation, and compact handoffs are now first-class.
- Ten language Pro Skills were added beyond existing `python-pro`.

### Decision
Future agents should treat `AGENTS.md` and `agent-team/` as canonical.

### Evidence
- `agent-team/protocols/communication.md` defines compact handoffs.
- `agent-team/skills/registry.md` registers categorized Skills.
- `docs/agent-memory/` stores project memory outside `agent-team/`.

### Next Action
Use this memory as orientation, then read `AGENTS.md` before making changes.

### Open Questions
Only the roadmap questions listed above.
