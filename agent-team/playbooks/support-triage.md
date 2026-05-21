# Support Triage Playbook

## Purpose

Convert a support ticket, customer report, bug report, or operator complaint into a compact triage artifact and route it to the right AgentCrew role.

Support triage helps product builders move from unstructured reports to clear severity, reproduction, owner, and next action without exposing raw customer data.

---

## When To Use

Use this playbook when:

```yaml
use_when:
  - user provides a support ticket or customer report
  - issue severity or priority is unclear
  - reproduction steps need to be captured
  - report may be bug, docs gap, feature request, product confusion, incident, or customer follow-up
  - impact assessment is needed before Developer work
```

---

## Triage Steps

```yaml
steps:
  - sanitize sensitive details
  - summarize the report
  - classify severity, impact, urgency, and confidence
  - capture reproduction evidence and environment
  - separate facts, assumptions, and open questions
  - identify specialist triggers
  - choose next owner and lane
  - write support triage report when durable context helps
```

---

## Routing

```yaml
route_to:
  developer: confirmed defect with actionable reproduction or likely code area
  tester: validation, reproduction, regression check, or environment confirmation
  product_manager: unclear expected behavior, priority, customer promise, or product tradeoff
  documentation_agent: docs gap, confusing instructions, examples, or release notes
  security_reviewer: security, privacy, auth, permissions, secrets, data, payments, or compliance risk
  release_manager: release regression, rollback, rollout, or release communication risk
  human: customer commitment, risk acceptance, escalation priority, or sensitive decision
```

---

## Artifact

Write project-specific support triage reports to:

```text
.agent-state/support-triage-report.md
```

Use:

```text
agent-team/templates/support-triage-report.md
```

---

## Safety

Do not store secrets, tokens, raw customer data, raw sensitive logs, personal identifiers, private paths, or customer commitments that the human has not approved.
