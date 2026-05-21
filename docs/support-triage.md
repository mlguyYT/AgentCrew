# Support Triage

## Purpose

Support triage gives AgentCrew a role for turning customer reports, support tickets, operator complaints, and bug reports into clear severity, reproduction, routing, and next action.

It helps product builders avoid jumping straight from a vague ticket into code changes.

---

## Use When

Use Support Triage Agent when a task involves:

- support tickets
- customer-reported bugs
- user complaints
- reproduction steps
- severity or impact assessment
- deciding whether something is bug, docs gap, feature request, incident, or product confusion

---

## Outputs

Project-specific support triage reports should live at:

```text
.agent-state/support-triage-report.md
```

Use:

```text
agent-team/agents/support-triage-agent.md
agent-team/playbooks/support-triage.md
agent-team/templates/support-triage-report.md
agent-team/checklists/support-triage.md
```

---

## Human Boundary

Agents may summarize, classify, route, and recommend next action.

Only the human may approve customer commitments, escalation priority, risk acceptance, public messaging, or final product decisions.
