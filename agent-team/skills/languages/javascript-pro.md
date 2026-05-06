# Skill: JavaScript Pro

## Purpose

Use this skill for professional JavaScript development in browsers, Node.js, tooling, and libraries.

## Applies when

Use this skill when work involves:

- JavaScript source files
- frontend behavior
- Node.js scripts
- package tooling
- module formats
- async JavaScript

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - JavaScript
    - JS
    - npm
    - async
  files:
    - "*.js"
    - "*.mjs"
    - "*.cjs"
    - "package.json"
    - "eslint.config.*"
  code_symbols:
    - Promise
    - async
    - await
    - module.exports
    - import
    - export
```

## Developer instructions

- Follow existing module style.
- Prefer simple functions and clear data flow.
- Handle async failures intentionally.
- Avoid hidden global state.
- Preserve browser or Node compatibility assumptions.
- Do not add dependencies for trivial utilities.
- Keep package script changes focused.

## Testing guidance

Look for:

```bash
npm test
npm run lint
npm run test
pnpm test
pnpm lint
yarn test
yarn lint
```

## Review checklist

- async flows handle errors
- module format is consistent
- changed behavior is tested
- browser/Node compatibility is preserved
- no unnecessary dependency was added
- no unrelated formatting churn

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - implicit globals
  - swallowed promise rejections
  - callback/promise mixing without need
  - package churn unrelated to task
  - large style-only rewrites
```

## Output note

If relevant, include:

```md
## Skills Applied
- javascript-pro
```
