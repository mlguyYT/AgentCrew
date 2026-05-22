# Customer Support Triage

## User Prompt

```text
Triage this customer bug report: checkout fails on mobile Safari after entering a coupon.
Severity is unclear. We need reproduction steps and next owner.
```

## Expected AgentCrew Routing

```yaml
starting_role: Support Triage Agent
intent: support_triage_or_customer_issue
recipe: bug-fix or incident depending on impact
next_roles:
  - Tester if reproduction is needed
  - Developer if defect is confirmed
  - Product Manager if expected behavior or priority is unclear
  - Security Reviewer if payment, data, auth, or privacy risk appears
  - Human for customer commitment or risk acceptance
```

## Expected Artifact

```text
.agent-state/support-triage-report.md
```

## Triage Focus

- sanitize customer data and logs
- identify affected user flow and environment
- capture reproduction steps and confidence
- classify severity, impact, and urgency
- route to the next owner

## Human Boundary

Agents may recommend severity and routing.
The human approves customer commitments, escalation priority, and risk acceptance.
