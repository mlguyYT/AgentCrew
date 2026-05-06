# Skill: React

## Purpose

Use this skill for React UI work, components, hooks, state management, and frontend behavior.

---

## Applies when

Use this skill when work involves:

- React components
- JSX or TSX
- hooks
- frontend forms
- UI state
- component tests
- Next.js or Vite React apps

---

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - React
    - component
    - hook
    - JSX
    - TSX
    - frontend
    - UI
  files:
    - "*.tsx"
    - "*.jsx"
    - "package.json"
    - "vite.config.*"
    - "next.config.*"
  code_symbols:
    - useState
    - useEffect
    - useMemo
    - useCallback
    - React.FC
```

---

## Developer instructions

When implementing React code:

- Follow existing component patterns.
- Keep components focused.
- Avoid unnecessary global state.
- Prefer clear props.
- Handle loading, empty, and error states when relevant.
- Avoid unnecessary re-renders for expensive components.
- Keep accessibility in mind.
- Do not introduce UI libraries unless explicitly requested.
- Preserve existing styling conventions.
- Avoid large unrelated formatting changes.

---

## Testing guidance

Look for project commands:

```bash
npm test
npm run test
npm run lint
npm run typecheck
pnpm test
pnpm lint
yarn test
```

Common tests:

- component renders
- user interaction works
- form validation
- loading/error states
- accessibility basics

---

## Review checklist

Reviewer should check:

- component is focused
- props are clear
- state is minimal
- hooks are used correctly
- dependency arrays are correct
- error/loading states are handled
- accessibility is not worsened
- tests cover changed behavior

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - unnecessary useEffect
  - duplicated state
  - prop drilling when existing pattern provides alternative
  - mixing unrelated UI refactors
  - introducing new state library without need
  - ignoring accessibility
```

---

## Output note

If relevant, include:

```md
## Skills Applied
- react
```
