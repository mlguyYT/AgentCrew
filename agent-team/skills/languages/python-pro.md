# Skill: Python Pro

## Purpose

Use this skill for high-quality Python development.

This skill can be used by Developer, Tester, and Reviewer agents.

---

## Applies when

Use this skill when work involves:

- Python source files
- Python APIs
- Python services
- Python tests
- Python packaging
- Python type checking
- Python linting
- Python performance
- async Python

---

## Detection triggers

Load this skill if the task or repo contains:

```yaml
triggers:
  text:
    - Python
    - pytest
    - ruff
    - mypy
    - asyncio
    - type hints
    - pyproject
  files:
    - "*.py"
    - "pyproject.toml"
    - "requirements.txt"
    - "setup.py"
    - "setup.cfg"
    - "pytest.ini"
    - "tox.ini"
    - "poetry.lock"
```

---

## Developer instructions

When implementing Python code:

- Prefer simple, readable, idiomatic Python.
- Follow existing project style.
- Use type hints for public functions when consistent with the project.
- Avoid clever abstractions.
- Keep functions small and purposeful.
- Prefer explicit error handling.
- Avoid hidden global state.
- Avoid mutable default arguments.
- Avoid broad `except Exception` unless justified.
- Preserve backward compatibility unless task requires change.
- Do not add dependencies unless clearly justified.

---

## Testing guidance

Prefer project-defined commands first.

Look for:

```text
Makefile
pyproject.toml
pytest.ini
tox.ini
README.md
.github/workflows
```

Common commands:

```bash
pytest
ruff check .
mypy .
python -m pytest
```

Only claim tests were run if they were actually run.

---

## Review checklist

Reviewer should check:

- code is readable
- naming is clear
- type hints are useful and not misleading
- exceptions are handled intentionally
- no mutable default arguments
- no unnecessary dependencies
- tests cover changed behavior
- async code is awaited correctly
- database/session/resource handling is safe
- public behavior changes are documented

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - large unrelated refactors
  - clever one-liners that hurt readability
  - swallowing exceptions silently
  - mutable defaults
  - hidden side effects on import
  - unnecessary class abstractions
  - adding dependencies for trivial logic
  - changing formatting across unrelated files
```

---

## Output note

If relevant, include:

```md
## Skills Applied
- python-pro
```
