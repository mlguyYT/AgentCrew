# Python Web App Preset

## Use When

Use for full-stack Python web apps (Django, Flask + Jinja, FastAPI + HTMX, Streamlit) where templates and static assets ship together with backend code.

Use the `python-api` preset for pure backend APIs without a server-rendered UI.

## Default Skills

```text
python-pro
sql-pro when persistence is touched
javascript-pro when HTMX, Alpine, or vanilla JS lives in templates
```

## Architecture Focus

- keep routing, business logic, persistence, and templates separated
- validate request and response boundaries explicitly
- never trust user input in templates — auto-escape by default, audit any `safe`
- isolate auth, session, and CSRF concerns
- preserve URL routes unless behavior change is approved

## Validation Defaults

- pytest with django.test.Client / TestClient when applicable
- ruff / mypy when configured
- integration tests for auth flows, database migrations, file uploads, payments
- accessibility check on touched templates when UX is a concern

## Review Gates

- dependency and supply-chain gate on requirements / pyproject changes
- compatibility rollout check on URL or template changes
- product behavior review when user-facing changes are non-trivial

## Required Specialists Suggestion

- Security Reviewer on auth, payment, file-upload, session, deserialization paths
- UX / Design Reviewer on template, layout, or interaction changes

## Config Defaults (suggested)

```yaml
quality_profile: standard
recipe_profiles:
  feature: strict
required_specialists:
  - paths: ["**/auth/**", "**/payments/**", "**/security/**"]
    roles: ["Security Reviewer"]
  - paths: ["templates/**", "**/static/**", "**/components/**"]
    roles: ["UX / Design Reviewer"]
```
