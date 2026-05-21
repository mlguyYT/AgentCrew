# Work Planning Playbook

## Purpose

Turn a routed request or task brief into a small, reviewable work plan before implementation starts.

Work planning helps product builders keep PRs small, separate risk decisions from implementation, and make the next developer action obvious.

---

## When To Use

Use this playbook when:

```yaml
use_when:
  - work may require more than one focused commit or PR
  - a feature needs slicing into implementation phases
  - a refactor must preserve behavior across boundaries
  - release, incident, or migration work needs visible sequencing
  - the user asks to plan, split, sequence, or break down work
```

For tiny one-file fixes, a full work plan is optional.

---

## Planning Rules

```yaml
planning_rules:
  - keep each phase small enough for focused review
  - separate discovery, implementation, validation, docs, and release work
  - put human-only decisions before implementation that depends on them
  - keep risky migrations, security changes, and compatibility work explicit
  - route implementation rework back to Developer
  - do not merge phases into one large PR unless the human explicitly accepts the review cost
```

---

## Phase Shape

Each phase should include:

```yaml
phase:
  id: WP-001
  owner: Product Manager | Developer | Tester | Reviewer | Specialist | Human
  goal: one clear outcome
  files_or_areas: likely areas, if known
  acceptance: observable completion condition
  validation: command, test type, or evidence expected
  gates: reviewer, specialist, or human approval triggers
```

---

## Command

Use the optional command:

```bash
~/AgentCrew/bin/agentcrew plan --project . --task "Add OAuth login"
```

Use `--dry-run` to preview and `--force` only when intentionally replacing `.agent-state/work-plan.md`.

---

## Artifact

Write project-specific work plans to:

```text
.agent-state/work-plan.md
```

Use:

```text
agent-team/templates/work-plan.md
```

Do not write work plans into `agent-team/` or the AgentCrew checkout when AgentCrew is guiding another project.
