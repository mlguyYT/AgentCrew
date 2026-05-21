# Incident Recipe

## Use For

Production issue, outage, urgent regression, rollback decision, data incident, security incident, or hotfix triage.

## Default Route

```text
Advisor or Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer -> Human
```

## Agent Focus

- stabilize first and avoid broad refactors
- separate mitigation, root cause, validation, and follow-up work
- record human-only risk decisions explicitly
- preserve evidence without storing secrets, raw customer data, or sensitive production data
- prefer small reversible fixes and clear rollback notes

## Escalate When

- customer data, security, payments, availability, compliance, or data-loss risk is involved
