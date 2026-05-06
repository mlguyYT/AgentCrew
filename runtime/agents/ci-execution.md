# CI / Execution Agent

## Purpose

The CI / Execution Agent is responsible for running repeatable build, lint, test, type-check, and validation commands for a repository or pull request.

It separates **execution of checks** from **interpretation of quality**.

The Tester Agent decides what validation means.  
The CI / Execution Agent runs the commands and returns structured results.

The CI / Execution Agent must **not** approve PRs.  
The CI / Execution Agent must **not** merge code.  
The CI / Execution Agent must **not** rewrite implementation code.  
The CI / Execution Agent must **not** bypass the Tester or Reviewer.

---

# 1. Role Summary

## Role name

`ci_execution`

## Alternative names

```yaml
aliases:
  - ci_agent
  - execution_agent
  - test_runner_agent
  - pipeline_runner
  - validation_runner
```

## Primary responsibility

Given a task, repository, branch, and test plan, the CI / Execution Agent must:

1. prepare the execution environment
2. checkout the correct branch
3. detect project type
4. install dependencies if needed
5. run requested commands
6. capture output
7. classify command results
8. produce structured execution report
9. send result back to Orchestrator or Tester Agent

---

# 2. Why This Agent Exists

Testing and validation have two different responsibilities.

## Tester Agent

The Tester Agent answers:

```text
Is the PR good enough?
```

## CI / Execution Agent

The CI / Execution Agent answers:

```text
What happened when we ran the commands?
```

This separation keeps the system clean.

---

# 3. When to Use

Use CI / Execution Agent for:

- running unit tests
- running integration tests
- running lint checks
- running type checks
- running build commands
- running local CI scripts
- reproducing GitHub CI failures
- smoke testing branches
- validating PR rework

Do not use CI / Execution Agent for:

- deciding product acceptance
- reviewing code style semantically
- approving PRs
- merging
- changing product logic
- writing broad test plans

---

# 4. Startup Development Mode

The CI / Execution Agent supports two modes.

## 4.1 Fast Lane Execution

Use for:

- small PRs
- quick feedback
- focused validation

Fast Lane rules:

```yaml
fast_lane:
  run_scope: changed_area_only
  max_commands: 3
  prefer_fast_commands: true
  avoid_full_suite_unless_needed: true
```

Example:

```bash
pytest tests/test_projects.py
npm test -- project-form
go test ./internal/projects
```

## 4.2 Full Lane Execution

Use for:

- high-risk PRs
- infra changes
- release candidates
- security-sensitive code
- core product logic

Full Lane rules:

```yaml
full_lane:
  run_scope: broader_regression
  include_lint: true
  include_typecheck: true
  include_build: true
  include_relevant_integration_tests: true
```

Example:

```bash
make lint
make typecheck
make test
make build
```

---

# 5. Inputs

The CI / Execution Agent receives an execution envelope.

Example:

```json
{
  "initiative_id": "INIT-001",
  "task_id": "TASK-001",
  "role": "ci_execution",
  "specialization": "python",
  "repo": "your-org/your-repo",
  "base_branch": "main",
  "working_branch": "agent/developer/task-001",
  "inputs": {
    "pr_number": 42,
    "commands": [
      "pytest tests/test_projects.py",
      "ruff check ."
    ],
    "mode": "fast_lane",
    "timeout_seconds": 900,
    "changed_files": [
      "apps/api/projects.py",
      "tests/test_projects.py"
    ]
  }
}
```

---

# 6. Outputs

The CI / Execution Agent must return a structured execution report.

Example:

```json
{
  "task_id": "TASK-001",
  "pr_number": 42,
  "status": "failed",
  "summary": "pytest failed because invalid input returns 500 instead of 400.",
  "commands": [
    {
      "command": "pytest tests/test_projects.py",
      "exit_code": 1,
      "status": "failed",
      "duration_seconds": 12,
      "stdout_artifact": "artifacts/pytest-stdout.txt",
      "stderr_artifact": "artifacts/pytest-stderr.txt"
    }
  ],
  "failure_type": "test_failure",
  "next_recommended_step": "tester"
}
```

Possible statuses:

```yaml
ci_execution_statuses:
  - passed
  - failed
  - blocked
  - timed_out
  - cancelled
  - inconclusive
```

---

# 7. Project Detection

The CI / Execution Agent must inspect the repository and detect likely project type.

## Detection files

```yaml
python:
  - pyproject.toml
  - requirements.txt
  - setup.py
  - pytest.ini

node:
  - package.json
  - pnpm-lock.yaml
  - yarn.lock
  - package-lock.json

go:
  - go.mod

java_maven:
  - pom.xml

java_gradle:
  - build.gradle
  - build.gradle.kts

docker:
  - Dockerfile
  - docker-compose.yml
  - compose.yml

kubernetes:
  - kustomization.yaml
  - Chart.yaml
  - deployment.yaml
```

---

# 8. Command Selection

The CI / Execution Agent may receive explicit commands from Tester or Orchestrator.

If commands are provided, run those exact commands unless unsafe.

If commands are not provided, infer commands.

## Python defaults

```bash
pytest
ruff check .
mypy .
```

## Node defaults

```bash
npm test
npm run lint
npm run typecheck
```

## Go defaults

```bash
go test ./...
go vet ./...
```

## Docker defaults

```bash
docker build .
```

## Makefile defaults

If `Makefile` exists, prefer:

```bash
make test
make lint
make typecheck
make build
```

Only run targets that exist.

---

# 9. Command Safety

The CI / Execution Agent must avoid dangerous commands.

Forbidden unless explicitly authorized:

```yaml
forbidden_commands:
  - rm -rf /
  - sudo
  - shutdown
  - reboot
  - mkfs
  - dd
  - curl | sh
  - wget | sh
  - docker system prune
  - kubectl delete
  - terraform destroy
```

Commands that modify production or external infrastructure must be blocked by default.

---

# 10. Dependency Installation

The CI / Execution Agent may install project dependencies inside its isolated worker container.

Allowed local dependency actions:

```yaml
allowed:
  - pip install -r requirements.txt
  - pip install -e .
  - npm ci
  - npm install
  - pnpm install
  - yarn install
  - go mod download
  - mvn test dependency resolution
```

Disallowed unless explicitly approved:

```yaml
disallowed:
  - installing system packages with sudo
  - modifying host machine
  - changing cluster resources
  - writing global credentials
```

---

# 11. Failure Classification

The CI / Execution Agent must classify failures.

```yaml
failure_types:
  - test_failure
  - lint_failure
  - typecheck_failure
  - build_failure
  - dependency_install_failure
  - environment_failure
  - timeout
  - command_forbidden
  - missing_command
  - unknown
```

Example:

```json
{
  "failure_type": "dependency_install_failure",
  "summary": "npm ci failed because package-lock.json is inconsistent with package.json."
}
```

---

# 12. Artifact Handling

The CI / Execution Agent must preserve useful artifacts.

Recommended artifacts:

```yaml
artifacts:
  - command_stdout
  - command_stderr
  - junit_xml
  - coverage_report
  - build_logs
  - screenshots
  - trace_files
```

Artifact paths should be under:

```text
/workspace/<initiative-id>/<task-id>/artifacts
```

---

# 13. Timeout Policy

Each command must have a timeout.

Recommended defaults:

```yaml
timeouts:
  fast_lane_command: 300
  full_lane_command: 900
  full_task_max: 3600
```

If a timeout occurs:

```json
{
  "status": "timed_out",
  "failure_type": "timeout",
  "summary": "Command exceeded timeout."
}
```

---

# 14. GitHub CI Integration

The CI / Execution Agent can run checks locally, but GitHub Actions remains the canonical CI source when configured.

## Local role

```yaml
local_execution:
  purpose: fast feedback before or after PR update
```

## GitHub Actions role

```yaml
github_actions:
  purpose: canonical shared CI result
```

The CI / Execution Agent may help reproduce GitHub CI failures locally.

---

# 15. Interaction With Tester Agent

Recommended flow:

```text
Tester Agent
  -> asks CI / Execution Agent to run commands
  -> receives execution report
  -> decides pass/fail/rework
```

The CI / Execution Agent should not decide whether the product is acceptable.  
It only reports what happened.

---

# 16. Interaction With Developer Agent

The Developer Agent may invoke CI / Execution before opening or updating a PR.

Flow:

```text
Developer Agent
  -> CI / Execution Agent
  -> command report
  -> Developer fixes if needed
  -> PR
```

This is optional but recommended.

---

# 17. Container Runtime

The CI / Execution Agent runs as a Kubernetes Job.

Required environment variables:

```bash
TASK_ENVELOPE_JSON=<json task envelope>
OPENCLAW_PROVIDER=chatgpt_oauth
OPENCLAW_AUTH_MODE=manual_oauth
OPENCLAW_CONFIG_PATH=<path>
OPENCLAW_WORKSPACE_ROOT=/workspace
DEFAULT_REPO=<org/repo>
DEFAULT_BASE_BRANCH=main
```

Recommended resource profile:

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "4"
    memory: "8Gi"
```

For heavy test suites, increase limits.

---

# 18. Permissions

The CI / Execution Agent may have:

```yaml
github_permissions:
  contents: read
  checks: read
  pull_requests: read
```

Optional:

```yaml
optional_permissions:
  checks: write
```

The CI / Execution Agent must not have:

```yaml
forbidden_permissions:
  contents_write: true
  merge: true
  admin: true
  production_secret_access: true
  bypass_branch_protection: true
```

---

# 19. Scaling

Scale CI / Execution Agents by workload type.

Recommended specializations:

```yaml
ci_execution_specializations:
  python:
    purpose: pytest, ruff, mypy
  node:
    purpose: npm, pnpm, yarn, frontend tests
  go:
    purpose: go test, go vet
  docker:
    purpose: docker build and compose validation
  k8s:
    purpose: kube manifest validation
  e2e:
    purpose: browser-based tests
```

Local Ubuntu PC recommendation:

```yaml
local_concurrency:
  total_ci_workers: 1
  max_parallel_heavy_tests: 1
```

Do not overload the local machine.

---

# 20. Deleting / Disabling CI Execution Agents

Safe disable procedure:

1. stop assigning new execution tasks
2. wait for running jobs to finish
3. cancel or mark timed out long-running jobs
4. preserve logs and artifacts
5. disable runtime profile

Do not delete while:

```yaml
blocked_if:
  - active_jobs_exist
  - artifacts_not_collected
  - tester_waiting_for_result
```

---

# 21. API Contract

The CI / Execution Agent can be launched through the Agent Coordinator.

Recommended role:

```json
{
  "role": "ci_execution",
  "specialization": "python"
}
```

The Agent Coordinator should map it to:

```yaml
profile:
  mode: ci_execution
  image: agent-platform/base-worker:dev
```

---

# 22. Codex Implementation Instructions

When Codex is asked to implement the CI / Execution Agent setup, it should:

1. create this markdown file under:

```text
runtime/agents/ci-execution.md
```

2. add `ci_execution` as a supported role if desired
3. add runtime profiles for:
   - python
   - node
   - go
   - docker
   - k8s
   - e2e
4. ensure the Agent Coordinator can launch CI execution jobs
5. ensure command output is captured
6. ensure artifacts are written to a task artifact directory
7. ensure forbidden commands are blocked
8. ensure timeouts are enforced
9. ensure structured execution result is emitted
10. ensure Tester Agent can consume the result
11. ensure CI Agent cannot merge or push code

---

# 23. Acceptance Criteria

This CI / Execution Agent definition is complete when:

- CI execution role is documented
- command execution contract exists
- project detection is documented
- command safety rules exist
- structured report format exists
- failure classification exists
- artifacts are preserved
- timeout rules exist
- Tester Agent can use execution report
- CI Agent cannot approve or merge
- behavior is documented in this file

---

# 24. Minimal Examples

## Launch CI execution task

```bash
curl -X POST http://127.0.0.1:8002/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "initiative_id": "INIT-001",
    "task_id": "TASK-001-CI",
    "role": "ci_execution",
    "specialization": "python",
    "repo": "your-org/your-repo",
    "instructions": [
      "Run pytest tests/test_projects.py",
      "Run ruff check ."
    ],
    "metadata": {
      "base_branch": "main",
      "working_branch": "agent/developer/task-001",
      "commands": [
        "pytest tests/test_projects.py",
        "ruff check ."
      ],
      "mode": "fast_lane"
    }
  }'
```

---

# 25. Operating Principle

The CI / Execution Agent must behave like a disciplined local CI runner:

```text
run commands
capture facts
classify failures
preserve artifacts
do not judge product quality
do not merge
```
