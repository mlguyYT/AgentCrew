# Skill: FastAPI

## Purpose

Use this skill for FastAPI applications, APIs, routers, dependencies, request validation, and response behavior.

This skill is more specific than `python-pro`.

If both apply, use both.

---

## Applies when

Use this skill when work involves:

- FastAPI app setup
- API endpoints
- routers
- request validation
- response models
- dependency injection
- Pydantic models
- Starlette middleware
- uvicorn app runtime

---

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - FastAPI
    - APIRouter
    - Depends
    - Pydantic
    - uvicorn
    - endpoint
    - route
  code_symbols:
    - fastapi.FastAPI
    - fastapi.APIRouter
    - fastapi.Depends
    - pydantic.BaseModel
  files:
    - "main.py"
    - "routers/*.py"
    - "api/*.py"
    - "schemas/*.py"
```

---

## Developer instructions

When implementing FastAPI code:

- Use existing router structure.
- Keep endpoint functions focused.
- Use Pydantic models for request/response validation when consistent with the project.
- Return appropriate HTTP status codes.
- Validate user input clearly.
- Avoid leaking internal exception details.
- Use dependency injection consistently.
- Keep business logic out of route handlers when existing architecture separates services.
- Preserve existing API behavior unless task requires change.
- Document breaking API changes.

---

## Status code guidance

Use appropriate status codes:

```yaml
status_codes:
  success_create: 201
  success_read: 200
  validation_error: 422_or_project_convention
  bad_request: 400
  unauthorized: 401
  forbidden: 403
  not_found: 404
  conflict: 409
  server_error: 500
```

Follow existing project conventions over generic preferences.

---

## Testing guidance

Common FastAPI tests use:

```python
from fastapi.testclient import TestClient
```

Test:

- successful request
- validation failure
- auth/permission behavior if relevant
- not found/conflict behavior if relevant
- response schema shape

Common commands:

```bash
pytest
pytest tests/
ruff check .
mypy .
```

---

## Review checklist

Reviewer should check:

- route belongs in correct router
- status codes are correct
- request validation is clear
- response schema is stable
- errors do not leak sensitive internals
- auth dependencies are preserved
- tests cover success and failure cases
- business logic is placed consistently with existing architecture

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - putting too much business logic in route functions
  - returning raw exceptions
  - inconsistent response shapes
  - bypassing dependencies
  - weakening auth checks
  - introducing untested validation behavior
```

---

## Output note

If relevant, include:

```md
## Skills Applied
- python-pro
- fastapi
```
