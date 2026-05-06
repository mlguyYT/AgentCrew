# Workflow: Idea → Task

## Purpose
Convert a raw idea into actionable tasks.

## Flow

```text
Idea
  -> Advisor (optional)
  -> Idea Consultant
  -> Human concept approval
  -> Product Manager
  -> Human backlog approval
```

---

## Step 1 — Idea input

Input can be:
- raw idea
- feature request
- problem statement

---

## Step 2 — Advisor (optional)

Used when:
- idea is unclear
- risk is high

Output:
- recommendation
- risks
- scope suggestions

---

## Step 3 — Idea Consultant

Creates structured idea brief using:
agent-team/templates/idea-brief.md

---

## Step 4 — Human concept approval

Human decides:
- proceed
- refine
- reject

---

## Step 5 — Product Manager

Creates:
- product plan
- tasks
- acceptance criteria

Using:
agent-team/templates/product-plan.md
agent-team/templates/task.md

---

## Step 6 — Human backlog approval

Human approves task breakdown before execution.

---

## Output

```yaml
output:
  - approved idea brief
  - product plan
  - task list
```
