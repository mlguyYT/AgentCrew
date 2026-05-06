# Skill Registry

## Purpose

This registry tells agents which skill files to load automatically.

Agents must inspect the task and repository context before acting.

When a task matches a skill trigger, load that skill file.

---

## Global rules

```yaml
rules:
  - match by explicit Skills field first
  - match by task text second
  - match by changed files and repository context third
  - load all matching skills
  - combine compatible skills
  - when skills conflict, prefer the more specific skill
  - never let a skill override human approval or safety rules
```

---

## Skill matching table

| Skill | File | Load when task mentions or touches |
|---|---|---|
| Python Pro | `languages/python-pro.md` | Python, `.py`, `pyproject.toml`, `requirements.txt`, `pytest`, `ruff`, `mypy`, `poetry.lock`, `setup.py` |
| TypeScript Pro | `languages/typescript-pro.md` | TypeScript, `.ts`, `.tsx`, `tsconfig.json`, type safety, typed API, `npm run typecheck`, `pnpm typecheck` |
| JavaScript Pro | `languages/javascript-pro.md` | JavaScript, `.js`, `.mjs`, `.cjs`, `package.json`, npm, async JavaScript, browser JS, Node.js scripts |
| SQL Pro | `languages/sql-pro.md` | SQL, `.sql`, migrations, queries, indexes, database schema, `SELECT`, `INSERT`, `UPDATE`, `JOIN` |
| Java Pro | `languages/java-pro.md` | Java, `.java`, `pom.xml`, `build.gradle`, Maven, Gradle, JVM services |
| C# Pro | `languages/csharp-pro.md` | C#, `.cs`, `.csproj`, `.sln`, dotnet, .NET, ASP.NET |
| C++ Pro | `languages/cpp-pro.md` | C++, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh`, `CMakeLists.txt`, native code |
| Go Pro | `languages/go-pro.md` | Go, Golang, `.go`, `go.mod`, `go.sum`, goroutines, `go test` |
| Rust Pro | `languages/rust-pro.md` | Rust, `.rs`, `Cargo.toml`, `Cargo.lock`, Cargo, borrow checker, async Rust |
| PHP Pro | `languages/php-pro.md` | PHP, `.php`, `composer.json`, `composer.lock`, Laravel, Symfony, PHPUnit |
| Shell Pro | `languages/shell-pro.md` | Shell, Bash, `.sh`, `scripts/**`, `Makefile`, CI shell commands, shellcheck |
| FastAPI | `frameworks/fastapi.md` | FastAPI, `APIRouter`, `Depends`, `pydantic`, `uvicorn`, `starlette`, API endpoint in Python |
| React | `frontend/react.md` | React, `.tsx`, `.jsx`, components, hooks, `useState`, `useEffect`, `vite`, `next`, `package.json` with React |
| Kubernetes | `platform/kubernetes.md` | Kubernetes, `k8s/`, `deployment.yaml`, `service.yaml`, `ingress.yaml`, Helm, Kustomize, `Chart.yaml`, `kustomization.yaml` |
| Reviewer Pro | `professional/reviewer-pro.md` | reviewer, review, code review, PR review, merge request review, maintainability, test adequacy, edge cases, approval readiness, rework request |
| Product Owner Pro | `professional/product-owner-pro.md` | Product Owner, PO, product ownership, product goal, product backlog, backlog, acceptance criteria, stakeholder, prioritization, roadmap, MVP, scope |

---

## Explicit skill syntax

Tasks may declare skills:

```md
## Skills
- python-pro
- fastapi
```

When explicit skills are present, load those files.

---

## Automatic detection examples

### Example 1

Task:

```text
Fix validation in a FastAPI endpoint.
```

Load:

```text
agent-team/skills/languages/python-pro.md
agent-team/skills/frameworks/fastapi.md
```

### Example 2

Changed files:

```text
src/components/Button.tsx
package.json
```

Load:

```text
agent-team/skills/frontend/react.md
agent-team/skills/languages/typescript-pro.md
```

### Example 3

Changed files:

```text
infra/k8s/deployment.yaml
infra/k8s/service.yaml
```

Load:

```text
agent-team/skills/platform/kubernetes.md
```

### Example 4

Task:

```text
Review this PR for risk, tests, and maintainability.
```

Load:

```text
agent-team/skills/professional/reviewer-pro.md
```

### Example 5

Task:

```text
Act as PO and turn this idea into a small backlog item with acceptance criteria.
```

Load:

```text
agent-team/skills/professional/product-owner-pro.md
```

---

## Skill priority

More specific skills override broader skills.

```yaml
priority_examples:
  fastapi_over_python:
    broader: python-pro
    specific: fastapi

  react_over_general_frontend:
    broader: frontend
    specific: react

  kubernetes_over_general_devops:
    broader: devops
    specific: kubernetes

  react_over_typescript_for_components:
    broader: typescript-pro
    specific: react

  product_owner_over_general_product_planning:
    broader: product_manager_role
    specific: product-owner-pro

  professional_reviewer_over_general_review:
    broader: reviewer_role
    specific: reviewer-pro
```

---

## Required agent behavior

Before implementation, testing, or review, the agent should state internally which skills apply.

When producing output for larger tasks, include a short note if useful:

```md
## Skills Applied
- python-pro
- fastapi
```

For small tasks, this can be omitted unless it helps the human understand the validation or implementation approach.
