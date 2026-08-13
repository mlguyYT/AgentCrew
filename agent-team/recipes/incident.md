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

## Runtime Contract

- Preserve volatile evidence and current state before commands that may alter it.
- Separate immediate mitigation from root-cause correction.
- Prefer reversible actions and define rollback before applying a risky change.
- Validate service health and the reported failure mode after mitigation.
- Record remaining exposure, follow-up work, and pending human decisions.

## Escalate When

- customer data, security, payments, availability, compliance, or data-loss risk is involved
