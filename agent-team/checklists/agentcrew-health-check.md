# AgentCrew Health Check

## Purpose

Use this checklist after installing or changing AgentCrew in a repository.

The goal is to verify that agents can find the workflow, apply the right lane, use Skills, hand off compactly, and preserve human approval.

---

## Root Files

- [ ] `AGENTS.md` exists
- [ ] `bin/agentcrew` exists and is executable
- [ ] `agent-team/` exists
- [ ] `README.md` or project docs explain how to use AgentCrew
- [ ] Optional tool adapters point to `AGENTS.md` and `agent-team/`
- [ ] Automatic-loading docs explain that AgentCrew should live outside target repositories

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
- [ ] `agent-team/agents/skill-validator.md`

---

## Required Playbooks

- [ ] `agent-team/playbooks/fast-lane.md`
- [ ] `agent-team/playbooks/full-lane.md`
- [ ] `agent-team/playbooks/pr-process.md`
- [ ] `agent-team/playbooks/rework-loop.md`
- [ ] `agent-team/playbooks/task-classification.md`
- [ ] `agent-team/playbooks/lane-escalation.md`
- [ ] `agent-team/playbooks/specialist-review-routing.md`
- [ ] `agent-team/playbooks/default-branch-merge.md`
- [ ] `agent-team/playbooks/dependency-supply-chain.md`
- [ ] `agent-team/playbooks/behavior-preserving-refactor.md`
- [ ] `agent-team/playbooks/compatibility-rollout.md`
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

---

## Required Tool Adapters

- [ ] `agent-team/adapters/README.md`
- [ ] `agent-team/adapters/claude-code.md`
- [ ] `agent-team/adapters/codex.md`
- [ ] `agent-team/adapters/openclaw.md`
- [ ] `agent-team/adapters/cursor.md`
- [ ] `agent-team/adapters/copilot.md`
- [ ] `docs/auto-load.md`

---

## Required Skills And Templates

- [ ] `agent-team/skills/registry.md`
- [ ] `agent-team/skills/authoring-guide.md`
- [ ] `agent-team/templates/pr-description.md`
- [ ] `agent-team/templates/test-report.md`
- [ ] `agent-team/templates/review-report.md`
- [ ] `agent-team/templates/security-review-report.md`
- [ ] `agent-team/templates/ux-design-review-report.md`
- [ ] `agent-team/templates/documentation-report.md`
- [ ] `agent-team/templates/memory-summary.md`
- [ ] `agent-team/templates/skill-validation-report.md`

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
