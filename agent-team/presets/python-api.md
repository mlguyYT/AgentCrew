# Python API Preset

## Use When

Use for FastAPI, Django, Flask, or Python backend services.

## Default Skills

```text
python-pro
fastapi when FastAPI is detected
sql-pro when persistence or migrations are touched
```

## Architecture Focus

- keep routing, business logic, persistence, and external integrations separated
- validate request and response boundaries explicitly
- preserve public API behavior unless behavior change is approved
- isolate configuration, secrets handling, and dependency clients

## Validation Defaults

- pytest when available
- ruff or equivalent lint command when available
- mypy or type checking when configured
- coverage gate when coverage tooling exists
- integration tests for database, queues, external services, filesystems, or auth flows

## Review Gates

- Security Reviewer for auth, permissions, secrets, customer data, dependencies, or production config
- Reviewer for API contracts, shared services, migrations, or behavior-changing refactors
- Documentation Agent when public API behavior or examples change
