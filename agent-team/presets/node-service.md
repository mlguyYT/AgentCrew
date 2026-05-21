# Node Service Preset

## Use When

Use for Express, Fastify, NestJS, server-side JavaScript, or TypeScript service repositories.

## Default Skills

```text
typescript-pro when TypeScript is present
javascript-pro
sql-pro when persistence or migrations are touched
```

## Architecture Focus

- keep handlers, domain logic, persistence, and external clients separated
- preserve protocol and API contracts unless behavior change is explicit
- avoid global mutable state for request-specific behavior
- keep runtime configuration and secrets out of source control

## Validation Defaults

- package-manager test command when available
- lint and typecheck commands when available
- build command when available
- audit command when dependencies or lockfiles change
- integration tests for databases, queues, sockets, timers, caches, or filesystem behavior

## Review Gates

- Security Reviewer for auth, permissions, secrets, customer data, dependency/runtime, or production config changes
- Reviewer for public API behavior, shared modules, async flow, or behavior-changing refactors
- Documentation Agent when public API behavior or examples change
