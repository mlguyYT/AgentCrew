# Workflow: Idea → Task

## Purpose
Convert a raw idea into a decision-ready direction and actionable tasks without asking the user to manage the team.

## Flow

```text
Idea
  -> Advisor
  -> Researcher Agent if evidence is needed
  -> Idea Consultant
  -> Product Manager
  -> Human direction and execution approval
```

---

## Step 1 — Idea input

Input can be:
- raw idea
- feature request
- problem statement

---

## Step 2 — Advisor

Used for idea direction, feasibility, value, and risk. AgentCrew invokes it automatically.

Output:
- recommendation
- risks
- scope suggestions

Researcher Agent supplies source-backed evidence here only when the decision depends on external facts.

---

## Step 3 — Idea Consultant

Creates structured idea brief using:
agent-team/templates/idea-brief.md

---

## Step 4 — Product Manager

Creates:
- product plan
- tasks
- acceptance criteria

Using:
agent-team/templates/product-plan.md
agent-team/templates/task.md

---

## Step 5 — Human direction and execution approval

AgentCrew presents one executive brief after discovery and planning. The human approves, refines, pauses, or rejects the direction and execution boundary before implementation.

Use separate concept, architecture, cost, or backlog gates only when the decisions cannot safely be combined.

---

## Output

```yaml
output:
  - approved idea brief
  - product plan
  - task list
  - executive brief
```

Continue with `agent-team/playbooks/idea-to-product.md` when implementation is requested.
