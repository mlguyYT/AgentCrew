# React Frontend Preset

## Use When

Use for React, Next.js, Vite, or component-heavy browser applications.

## Default Skills

```text
typescript-pro
react
javascript-pro when plain JS is present
```

## Architecture Focus

- keep UI components small and composable
- separate presentation, state, data fetching, and routing concerns
- preserve accessibility, responsive behavior, and keyboard flows
- avoid mixing product copy, API logic, and visual state in one component

## Validation Defaults

- package-manager test command when available
- lint command when available
- build or typecheck command when available
- coverage gate when coverage tooling exists

## Review Gates

- UX / Design Reviewer for user-facing flow, layout, accessibility, or responsive changes
- Reviewer for shared components, routing, state management, or behavior-changing refactors
- Security Reviewer for auth, tokens, customer data, or dependency/runtime changes
