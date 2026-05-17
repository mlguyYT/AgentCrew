# FAQ

## Does this require Codex?

No.

This workflow is tool-agnostic. It can be used with any AI coding agent that reads repository instructions.

---

## Does this require Docker or Kubernetes?

No.

This is a Markdown-based workflow. Docker and Kubernetes are not required.

---

## Is AgentCrew a runtime?

No.

AgentCrew is a lightweight instruction system by default. It can be extended with automation later, but the core package is Markdown files.

---

## Can agents merge PRs?

No.

By default, agents must not merge. Human approval and merge are required.

---

## Is this only for startups?

No.

It is optimized for startup-style speed, but any team can use it.

---

## Should every task use every agent?

No.

AgentCrew should classify the request and use Fast Lane by default.

Only use the full team for risky or complex work.

---

## Do I have to tell AgentCrew which role to use?

No.

You can ask a normal question or request an outcome:

```text
Fix the empty-email validation bug.
```

AgentCrew should choose the lane, role, and Skills automatically.

Explicit role prompts are still useful when you want manual control.

---

## What if the agent ignores the instructions?

Make the root `AGENTS.md` shorter and more explicit.

First check whether automatic loading is registered:

```bash
~/AgentCrew/bin/agentcrew status
```

If the tool still ignores AgentCrew, use the relevant adapter in:

```text
agent-team/adapters/
```

As a temporary fallback, repeat the routing instruction in your prompt:

```text
Classify this request, choose the right AgentCrew role and Skills, and follow the matching playbook.
```

---

## Can I add new agents?

Yes.

Add a new file under:

```text
agent-team/agents/
```

Then update:

```text
AGENTS.md
```

---

## How do I add a new Skill?

Read the authoring guide:

```text
agent-team/skills/authoring-guide.md
```

Then add the Skill under the right category in:

```text
agent-team/skills/
```

Then update:

```text
agent-team/skills/registry.md
```

Validate it with:

```text
agent-team/agents/skill-validator.md
agent-team/playbooks/skill-validation.md
```

---

## Where should agents save memory?

Use the human's preferred memory system.

For committed project memory, use a project-owned folder such as:

```text
docs/agent-memory/
```

Do not store project memory inside `agent-team/`.

Use `.agent-state/` for current handoff state:

```text
.agent-state/current-task.md
.agent-state/decisions.md
.agent-state/handoff.md
.agent-state/test-report.md
.agent-state/review-report.md
.agent-state/memory.md
```

Follow `agent-team/protocols/state-artifacts.md`.

---

## Can I use this with GitHub Issues?

Yes.

Use the task template in issue descriptions.

---

## Can I use this without PRs?

Yes, but PRs are recommended because they make quality and review visible.

---

## What is the smallest useful external setup?

```text
~/AgentCrew/AGENTS.md
~/AgentCrew/agent-team/agents/developer.md
~/AgentCrew/agent-team/agents/tester.md
~/AgentCrew/agent-team/agents/reviewer.md
~/AgentCrew/agent-team/playbooks/fast-lane.md
~/AgentCrew/agent-team/playbooks/pr-process.md
~/AgentCrew/agent-team/playbooks/rework-loop.md
~/AgentCrew/agent-team/playbooks/memory-saving.md
~/AgentCrew/agent-team/skills/registry.md
~/AgentCrew/agent-team/templates/task.md
~/AgentCrew/agent-team/templates/pr-description.md
~/AgentCrew/agent-team/templates/test-report.md
~/AgentCrew/agent-team/templates/review-report.md
~/AgentCrew/agent-team/templates/memory-summary.md
```
