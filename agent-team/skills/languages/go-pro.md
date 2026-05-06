# Skill: Go Pro

## Purpose

Use this skill for professional Go development in services, CLIs, libraries, tests, and tooling.

## Applies when

Use this skill when work involves:

- Go source files
- Go modules
- HTTP services
- goroutines and channels
- context cancellation
- Go tests

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - Go
    - Golang
    - go test
    - goroutine
  files:
    - "*.go"
    - "go.mod"
    - "go.sum"
  code_symbols:
    - context.Context
    - goroutine
    - go func
    - defer
```

## Developer instructions

- Prefer simple, idiomatic Go.
- Pass `context.Context` through request-scoped operations.
- Return errors with useful context.
- Keep interfaces small and consumer-owned.
- Avoid goroutine leaks.
- Use table-driven tests when helpful.
- Do not add dependencies without clear need.

## Testing guidance

Look for:

```bash
go test ./...
go test -race ./...
go vet ./...
gofmt -w
```

Only run race tests when practical for the task.

## Review checklist

- errors are handled explicitly
- contexts are propagated
- goroutines can exit
- interfaces are not overabstracted
- tests cover changed behavior
- formatting is gofmt-compliant

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - ignored errors
  - goroutine leaks
  - package-level mutable state
  - oversized interfaces
  - panic for normal error handling
```

## Output note

If relevant, include:

```md
## Skills Applied
- go-pro
```
