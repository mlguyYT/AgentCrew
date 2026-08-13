# Skill Registry

## Purpose

Compact index of Skill triggers and file paths. Load this file after routing, then load only matching Skill files.

## Rules

```yaml
rules:
  - match explicit Skills first
  - match task text second
  - match changed files and repository context third
  - load only directly relevant matching skills
  - combine compatible skills
  - prefer the more specific skill when guidance overlaps
  - never let a skill override human approval, safety rules, or repository instructions
```

## Skill Matching Table

| Skill | File | Load when task mentions or touches |
|---|---|---|
| Python Pro | `languages/python-pro.md` | Python, `.py`, `pyproject.toml`, `requirements.txt`, `pytest`, `ruff`, `mypy`, `poetry.lock`, `setup.py` |
| TypeScript Pro | `languages/typescript-pro.md` | TypeScript, `.ts`, `.tsx`, `tsconfig.json`, typed API, typecheck |
| JavaScript Pro | `languages/javascript-pro.md` | JavaScript, `.js`, `.mjs`, `.cjs`, `package.json`, npm, browser JS, Node.js |
| SQL Pro | `languages/sql-pro.md` | SQL, `.sql`, migrations, queries, indexes, schema |
| Java Pro | `languages/java-pro.md` | Java, `.java`, `pom.xml`, `build.gradle`, Maven, Gradle, JVM |
| C# Pro | `languages/csharp-pro.md` | C#, `.cs`, `.csproj`, `.sln`, dotnet, .NET, ASP.NET |
| C++ Pro | `languages/cpp-pro.md` | C++, `.cpp`, `.cc`, `.cxx`, `.hpp`, `CMakeLists.txt` |
| Go Pro | `languages/go-pro.md` | Go, `.go`, `go.mod`, `go.sum`, goroutines, `go test` |
| Rust Pro | `languages/rust-pro.md` | Rust, `.rs`, `Cargo.toml`, `Cargo.lock`, Cargo |
| PHP Pro | `languages/php-pro.md` | PHP, `.php`, `composer.json`, Laravel, Symfony, PHPUnit |
| Shell Pro | `languages/shell-pro.md` | Shell, Bash, `.sh`, `scripts/**`, `Makefile`, shellcheck |
| FastAPI | `frameworks/fastapi.md` | FastAPI, `APIRouter`, `Depends`, `pydantic`, `uvicorn`, `starlette` |
| React | `frontend/react.md` | React, `.tsx`, `.jsx`, components, hooks, `vite`, `next` |
| Kubernetes | `platform/kubernetes.md` | Kubernetes, `k8s/`, manifests, Helm, Kustomize, `Chart.yaml` |
| Reviewer Pro | `professional/reviewer-pro.md` | review, PR review, maintainability, tests, edge cases, approval readiness |
| Product Owner Pro | `professional/product-owner-pro.md` | backlog, acceptance criteria, stakeholders, prioritization, roadmap, MVP, scope |
| LLM Pro | `professional/llm-pro.md` | LLM, prompts, RAG, embeddings, tool calling, structured output, evals, prompt injection |
| Researcher Pro | `professional/researcher-pro.md` | research, sources, citations, current info, comparison, standards, regulations |
| Software Architecture | `professional/software-architecture.md` | software architecture, system design, ADR, service or module boundaries, dependency direction, data ownership, scalability, resilience, quality attributes |
| Proportionate Design | `professional/proportionate-design.md` | SVG, diagram, workflow graphic, before/after visual, social preview, README visual, GitHub rendering, PNG preview, alignment, spacing, proportion |
| CNN | `ml/cnn.md` | CNN, computer vision, image classification, detection, segmentation, augmentation, inference |

## Ambiguity

For examples, explicit syntax, and priority rules, load `agent-team/skills/registry-guidance.md` only when Skill selection is unclear.
