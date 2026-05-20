# AgentCrew Health Check

## Purpose

Use this checklist after installing or changing AgentCrew in a repository.

The goal is to verify that agents can find the workflow, apply the right lane, use Skills, hand off compactly, and preserve human approval.

---

## Automated Check

- [ ] Run `bin/agentcrew doctor` from the AgentCrew checkout
- [ ] Confirm the summary reports zero failures
- [ ] Review warnings and decide whether they are expected for the environment

---

## Root Files

- [ ] `AGENTS.md` exists
- [ ] `bin/agentcrew` exists and is executable
- [ ] `bin/agentcrew doctor` reports zero failures
- [ ] `bin/agentcrew detect-project --project .` runs from a target project
- [ ] `bin/agentcrew classify "Fix a small bug" --project .` returns a route
- [ ] `bin/agentcrew status --project .` shows registrations and project dashboard
- [ ] `agent-team/` exists
- [ ] `README.md` or project docs explain how to use AgentCrew
- [ ] Optional tool adapters point to `AGENTS.md` and `agent-team/`
- [ ] Automatic-loading docs explain that AgentCrew should live outside target repositories

---

## Required Context Files

- [ ] `agent-team/context/route-index.md`
- [ ] `agent-team/context/fast-lane-context.md`
- [ ] `agent-team/context/full-lane-context.md`
- [ ] `agent-team/context/review-context.md`
- [ ] `agent-team/context/research-context.md`

---

## Required Role Files

- [ ] `agent-team/agents/advisor.md`
- [ ] `agent-team/agents/idea-consultant.md`
- [ ] `agent-team/agents/product-manager.md`
- [ ] `agent-team/agents/developer.md`
- [ ] `agent-team/agents/tester.md`
- [ ] `agent-team/agents/reviewer.md`
- [ ] `agent-team/agents/security-reviewer.md`
- [ ] `agent-team/agents/ux-design-reviewer.md`
- [ ] `agent-team/agents/documentation-agent.md`
- [ ] `agent-team/agents/llm-agent.md`
- [ ] `agent-team/agents/researcher-agent.md`
- [ ] `agent-team/agents/cnn-agent.md`
- [ ] `agent-team/agents/skill-validator.md`

---

## Required Playbooks

- [ ] `agent-team/playbooks/fast-lane.md`
- [ ] `agent-team/playbooks/full-lane.md`
- [ ] `agent-team/playbooks/pr-process.md`
- [ ] `agent-team/playbooks/rework-loop.md`
- [ ] `agent-team/playbooks/task-classification.md`
- [ ] `agent-team/playbooks/request-routing.md`
- [ ] `agent-team/playbooks/human-decision-queue.md`
- [ ] `agent-team/playbooks/lane-escalation.md`
- [ ] `agent-team/playbooks/specialist-review-routing.md`
- [ ] `agent-team/playbooks/default-branch-merge.md`
- [ ] `agent-team/playbooks/dependency-supply-chain.md`
- [ ] `agent-team/playbooks/behavior-preserving-refactor.md`
- [ ] `agent-team/playbooks/compatibility-rollout.md`
- [ ] `agent-team/playbooks/token-safe-mode.md`
- [ ] `agent-team/playbooks/skill-loading.md`
- [ ] `agent-team/playbooks/skill-validation.md`
- [ ] `agent-team/playbooks/memory-saving.md`

---

## Required Protocols And Conventions

- [ ] `agent-team/protocols/communication.md`
- [ ] `agent-team/protocols/handoff-format.md`
- [ ] `agent-team/protocols/token-discipline.md`
- [ ] `agent-team/protocols/state-artifacts.md`
- [ ] `agent-team/conventions/naming.md`
- [ ] `agent-team/checklists/shared-memory-refresh.md`
- [ ] `agent-team/checklists/integration-test-escalation.md`
- [ ] `agent-team/checklists/llm-review.md`
- [ ] `agent-team/checklists/research-quality.md`
- [ ] `agent-team/checklists/cnn-review.md`

---

## Required Tool Adapters

- [ ] `agent-team/adapters/README.md`
- [ ] `agent-team/adapters/claude-code.md`
- [ ] `agent-team/adapters/codex.md`
- [ ] `agent-team/adapters/openclaw.md`
- [ ] `agent-team/adapters/cursor.md`
- [ ] `agent-team/adapters/copilot.md`
- [ ] `docs/auto-load.md`
- [ ] `docs/doctor.md`
- [ ] `docs/project-detection.md`
- [ ] `docs/task-classifier.md`
- [ ] `docs/status-dashboard.md`
- [ ] `docs/human-decision-queue.md`

---

## Required Skills And Templates

- [ ] `agent-team/skills/registry.md`
- [ ] `agent-team/skills/authoring-guide.md`
- [ ] `agent-team/skills/professional/llm-pro.md`
- [ ] `agent-team/skills/professional/researcher-pro.md`
- [ ] `agent-team/skills/ml/cnn.md`
- [ ] `agent-team/templates/task-routing.md`
- [ ] `agent-team/templates/human-decision-queue.md`
- [ ] `agent-team/templates/pr-description.md`
- [ ] `agent-team/templates/test-report.md`
- [ ] `agent-team/templates/review-report.md`
- [ ] `agent-team/templates/security-review-report.md`
- [ ] `agent-team/templates/ux-design-review-report.md`
- [ ] `agent-team/templates/documentation-report.md`
- [ ] `agent-team/templates/compact-handoff.md`
- [ ] `agent-team/templates/compact-test-report.md`
- [ ] `agent-team/templates/compact-review-report.md`
- [ ] `agent-team/templates/compact-research-report.md`
- [ ] `agent-team/templates/llm-report.md`
- [ ] `agent-team/templates/research-report.md`
- [ ] `agent-team/templates/cnn-report.md`
- [ ] `agent-team/templates/memory-summary.md`
- [ ] `agent-team/templates/skill-validation-report.md`
- [ ] `agent-team/tools/classify-task.sh`
- [ ] `agent-team/tools/detect-project.sh`
- [ ] `agent-team/tools/project-status.sh`

---

## Safety Rules

- [ ] Human approval rule exists
- [ ] No-autonomous-merge rule exists
- [ ] Agents may not bypass branch protection
- [ ] Agents may not commit secrets
- [ ] Agents may not hide test failures
- [ ] Security or data-risk tradeoffs require human decision
- [ ] Data-loss, migration, public-behavior, insecure legacy compatibility, and shared-history rewrite decisions require human decision

---

## Runtime Independence

- [ ] Core workflow does not require Docker
- [ ] Core workflow does not require Kubernetes
- [ ] Core workflow does not require a GitHub App
- [ ] Optional runtime references are clearly labeled as optional

---

## Recommendation

If any required item is missing, fix the workflow package before relying on AgentCrew for implementation work.

If runtime assumptions appear in core files, move them to `runtime/` or mark them optional.
