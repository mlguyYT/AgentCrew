# Feature Recipe

## Use For

New or changed product capability.

## Default Route

```text
Product Manager -> Developer -> Tester -> Reviewer -> Human
```

## Agent Focus

- clarify acceptance criteria before implementation
- split work into small PR-sized tasks
- identify user-visible behavior and rollout needs
- keep data model, API, and UI changes scoped
- update docs or examples when public behavior changes

## Runtime Contract

- Map each acceptance criterion to an implementation boundary and a check.
- Inspect existing extension points before introducing a new abstraction.
- Implement the smallest end-to-end behavior slice first.
- Verify the primary path, relevant edge cases, and compatibility expectations.
- Record intentionally deferred scope instead of partially implementing it.

## Escalate When

- product direction is unclear
- compatibility, migration, data, security, billing, or rollout risk appears
- the feature becomes too large for a focused PR
