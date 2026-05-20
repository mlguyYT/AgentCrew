# Project Detection

## Purpose

`agentcrew detect-project` inspects a target project and prints a compact profile that helps AgentCrew choose relevant Skills and validation gates.

It is read-only. It does not copy AgentCrew into the project and does not create project configuration.

---

## Run

From a project directory:

```bash
~/AgentCrew/bin/agentcrew detect-project
```

From anywhere:

```bash
~/AgentCrew/bin/agentcrew detect-project --project /path/to/project
```

The standalone tool is also available inside AgentCrew:

```bash
~/AgentCrew/agent-team/tools/detect-project.sh --project /path/to/project
```

---

## What It Detects

The detector looks for common signals:

- git repository, current branch, default branch, and HEAD
- languages such as Python, TypeScript, JavaScript, Go, Rust, Java/Kotlin, C#, C/C++, PHP, SQL, and Shell
- frameworks and platforms such as React, Next.js, Vite, FastAPI, Django, Flask, Node API, containers, Kubernetes, and CI/CD
- package managers and lockfiles
- likely validation commands
- coverage tooling hints
- suggested AgentCrew Skills

The output is intentionally compact so agents can use it as routing context without loading the whole repository into the conversation.

---

## How Agents Should Use It

Agents should treat the profile as a starting point. Before implementation, they still need to inspect the task, relevant files, changed files, and repository instructions.

Use the detected profile to decide:

- which Skills to load from `agent-team/skills/registry.md`
- which validation commands are likely relevant
- whether coverage tooling exists
- whether platform, dependency, or supply-chain gates may apply

Do not treat missing detection as proof that a technology is absent. Small projects, generated code, monorepos, or unusual layouts may need manual inspection.

---

## Example

```text
# AgentCrew Project Profile

## Detected Stack

- languages: TypeScript, Python
- frameworks: React, FastAPI
- package_managers: pnpm, pyproject

## Suggested AgentCrew Skills

- typescript-pro
- react
- python-pro
- fastapi
```

For a request like `Fix the dashboard filter bug`, AgentCrew can start with the Developer role, load TypeScript/React guidance, then run the detected validation commands when relevant.

---

## Pair With Classification

After detecting the project profile, classify a request against that project:

```bash
~/AgentCrew/bin/agentcrew classify --project /path/to/project --task "Add OAuth login"
```
