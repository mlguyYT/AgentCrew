# Skill: TypeScript Pro

## Purpose

Use this skill for professional TypeScript development across frontend, backend, libraries, and tooling.

## Applies when

Use this skill when work involves:

- TypeScript source files
- typed public APIs
- frontend or backend TypeScript
- `tsconfig.json`
- type checking
- TypeScript refactors

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - TypeScript
    - type safety
    - tsconfig
    - typed API
  files:
    - "*.ts"
    - "*.tsx"
    - "tsconfig.json"
    - "package.json"
  code_symbols:
    - interface
    - type
    - satisfies
    - as const
```

## Developer instructions

- Follow existing project style.
- Prefer accurate types over broad assertions.
- Avoid `any` unless justified.
- Keep public types stable unless the task requires a breaking change.
- Use discriminated unions for state that has clear variants.
- Avoid duplicating runtime and compile-time schemas when the project has a shared validation pattern.
- Do not add dependencies for trivial type utilities.

## Testing guidance

Look for:

```bash
npm run typecheck
npm run lint
npm test
pnpm typecheck
pnpm lint
pnpm test
yarn typecheck
yarn test
```

## Review checklist

- types model real runtime behavior
- no unnecessary `any` or unsafe assertions
- public API compatibility is considered
- null/undefined paths are handled
- async errors are handled intentionally
- typecheck/lint/test results are documented

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - broad any usage
  - type assertions hiding real errors
  - changing generated files manually
  - unrelated formatting churn
  - weakening strictness to pass checks
```

## Output note

If relevant, include:

```md
## Skills Applied
- typescript-pro
```
