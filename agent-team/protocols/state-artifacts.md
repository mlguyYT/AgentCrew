# State Artifacts

## Purpose

State artifacts preserve current work context between agents and sessions.

They are project working state. They are not part of the reusable AgentCrew methodology.

---

## Folder Rule

Use:

```text
.agent-state/
```

Do not store project-specific state in:

```text
agent-team/
```

`agent-team/` is reusable methodology. `.agent-state/` is local project context.

Each project owns its own `.agent-state/` folder.
Agents must not share one `.agent-state/` folder across multiple target projects.
When AgentCrew is loaded from an external checkout, state still belongs in the target project, not in the AgentCrew checkout.

---

## Recommended Files

```text
.agent-state/
  sessions/
  project-constraints.md
  current-task.md
  project-preset.md
  artifact-map.md
  cloud-resources.md
  eval-metrics.md
  task-brief.md
  work-plan.md
  readiness-report.md
  pr-pack.md
  decisions.md
  human-decisions.md
  handoff.md
  test-report.md
  review-report.md
  security-review-report.md
  ux-design-review-report.md
  documentation-report.md
  support-triage-report.md
  release-report.md
  llm-report.md
  research-report.md
  cnn-report.md
  skill-validation-report.md
  role-fit-matrix.md
  mvp-scope.md
  resume-bullets.md
  demo-script.md
  memory.md
```

Use only the files that are useful for the current project. `agentcrew start` can create `current-task.md`; `agentcrew status` reads these files when present and reports missing files as `not set`.

If `project-constraints.md` exists, agents should read it before action and summarize active no-commit, no-push, public/private, cloud, or sensitive wording constraints in work summaries.

`sessions/` stores timestamped local session checkpoints created by the optional AgentCrew save-session and checkpoint utilities.
The save-session utility resolves the target git repository root automatically, so checkpoints from different projects do not conflict.
Structured checkpoint blocks use `agent-team/protocols/checkpoint-blocks.md`.

---

## File Purposes

```yaml
current-task.md:
  purpose: active task, acceptance criteria, lane, and owner

project-constraints.md:
  purpose: standing project guardrails such as workflow boundary, commit/push mode, public/private boundary, cloud teardown rules, sensitive wording, and next safe action

project-preset.md:
  purpose: selected project-shape preset with default Skills, validation, review gates, and architecture focus

artifact-map.md:
  purpose: classification of planned or generated artifacts as public repo, private local note, ignored runtime file, cloud resource, or temporary log/output

cloud-resources.md:
  purpose: cost confirmation, active cloud resources, endpoints, teardown commands, deletion verification, and remaining cloud risk

eval-metrics.md:
  purpose: baseline and current evaluation metrics, command, dataset, delta, and acceptance status

task-brief.md:
  purpose: scoped task brief with provisional acceptance criteria, scope, test plan, gates, and open questions

work-plan.md:
  purpose: PR-sized implementation phases, owners, validation, gates, risks, and next action

readiness-report.md:
  purpose: implementation-readiness decision, blockers, warnings, recommendation, and next action

pr-pack.md:
  purpose: compact PR preparation packet with task, validation, review, risk, and human-approval evidence

decisions.md:
  purpose: durable human or agent decisions with dates

human-decisions.md:
  purpose: pending and resolved human-only decisions surfaced by `agentcrew status`

handoff.md:
  purpose: compact current handoff between roles

test-report.md:
  purpose: latest Tester evidence

review-report.md:
  purpose: latest Reviewer findings

security-review-report.md:
  purpose: latest Security Reviewer findings

ux-design-review-report.md:
  purpose: latest UX / Design Reviewer findings

documentation-report.md:
  purpose: latest Documentation Agent findings

support-triage-report.md:
  purpose: latest Support Triage Agent severity, impact, evidence, routing, and next-action summary

release-report.md:
  purpose: latest Release Manager readiness, rollout, rollback, risk, and human-decision summary

llm-report.md:
  purpose: latest LLM Agent findings for prompts, RAG, model behavior, tool use, evaluations, and LLM safety

research-report.md:
  purpose: latest Researcher Agent source-backed findings, assumptions, confidence, and open questions

cnn-report.md:
  purpose: latest CNN Agent findings for computer vision architecture, datasets, training, evaluation, and inference

skill-validation-report.md:
  purpose: latest Skill Validator findings for new or changed Skills and registry updates

role-fit-matrix.md:
  purpose: target-role requirements mapped to project features, evidence artifacts, interview talking points, and over-scope risks

mvp-scope.md:
  purpose: minimum convincing portfolio project scope, out-of-scope ideas, technical evidence, and human scope approval state

resume-bullets.md:
  purpose: human-approved resume or portfolio claims with links to supporting evidence

demo-script.md:
  purpose: concise demo flow, technical talking points, caveats, and questions to prepare for

memory.md:
  purpose: short project context worth preserving between sessions

sessions/:
  purpose: timestamped local checkpoints and optional [agentcrew-context] blocks for pause/resume across agent sessions
```

---

## Handoff Schema

Use the format from `agent-team/protocols/handoff-format.md`:

```md
### Context
- 1-3 bullets only.

### Decision
What was decided.

### Evidence
- Only facts needed by the next agent.

### Next Action
Exactly what the next agent should do.

### Open Questions
Only blockers.
```

---

## Human Decision Queue Schema

Use:

```text
agent-team/templates/human-decision-queue.md
```

Store project-specific queues at:

```text
.agent-state/human-decisions.md
```

Only the human may mark risk-acceptance decisions as approved, rejected, or deferred.

---

## Current Task Schema

Use `agent-team/templates/current-task.md` as the canonical template.


```md
# Current Task

## Title

## Lane
Fast Lane / Full Lane

## Risk
Low / Medium / High / Critical

## Quality Profile
Light / Standard / Strict / Regulated

## Recipe
bug-fix / feature / refactor / docs-update / review / validation / research / portfolio-project / release / incident / skill-change

## Owner
Developer / Tester / Reviewer / Specialist / Human

## Acceptance Criteria
- criterion

## Status
Current state.

## Next Action
Exactly what should happen next.
```

---

## Safety

State artifacts must not include:

- secrets
- tokens
- passwords
- private keys
- private key paths
- deploy-key paths
- personal Git identity
- personal email addresses
- local machine paths
- workstation-specific auth commands
- raw customer data
- sensitive production data
- long logs
- hidden reasoning traces

If a secret is discovered, follow `agent-team/policies/secrets-policy.md`.

---

## Git Policy

`.agent-state/` is usually gitignored.

If a project intentionally commits state artifacts, keep them short, factual, dated, and free of sensitive data.
Committed state must be team-neutral.

Before committing or updating shared state, refresh:

- current default branch
- current HEAD
- current validation baseline
- current open risks
- current next steps

Remove stale phase notes, personal/local setup, secrets, and private paths.

Use:

```text
agent-team/checklists/shared-memory-refresh.md
```
