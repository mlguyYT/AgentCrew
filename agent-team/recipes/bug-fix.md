# Bug Fix Recipe

## Use For

Focused fixes where expected behavior is known.

## Default Route

```text
Developer -> Tester -> Reviewer when risk is meaningful -> Human
```

## Agent Focus

- reproduce or understand the defect before changing code
- keep the fix narrow
- add or update a regression test when practical
- preserve unrelated behavior
- document test limitations when validation is incomplete

## Runtime Contract

- Establish a failing baseline or capture why reproduction is unavailable.
- Trace the failure to a specific cause before editing.
- Change the smallest boundary that corrects the cause.
- Add or run a regression check that fails before the fix and passes after it.
- Recheck adjacent behavior and inspect the final diff for unrelated changes.

## Escalate When

- root cause touches auth, billing, customer data, migrations, infrastructure, public APIs, dependencies, or shared modules
- the fix changes user-visible behavior beyond the reported bug
- the defect suggests a broader architecture issue
