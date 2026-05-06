# Agent Coordinator / Runtime Manager

## Purpose

The Agent Coordinator is the runtime bridge between the Orchestrator and the actual agent execution environments.

The Orchestrator decides **what should happen**.  
The Agent Coordinator decides **how to run it safely**.

The Agent Coordinator is responsible for:

1. receiving task dispatch requests from the Orchestrator
2. selecting the correct runtime profile
3. launching Kubernetes Jobs or Docker containers
4. injecting the task envelope
5. injecting role and specialization configuration
6. injecting OpenClaw runtime configuration
7. tracking execution status
8. collecting structured worker results
9. returning execution status to the Orchestrator
10. enforcing runtime safety rules

The Agent Coordinator is not a product agent.  
It does not decide strategy.  
It does not write product specs.  
It does not review code.  
It does not approve PRs.  
It does not merge code.

---

# 1. Component Summary

## Component name

`agent_coordinator`

## Alternative names

```yaml
aliases:
  - runtime_manager
  - execution_coordinator
  - worker_launcher
  - agent_runtime_controller
```

## Primary responsibility

The Agent Coordinator converts this:

```json
{
  "task_id": "TASK-001",
  "role": "developer",
  "specialization": "backend"
}
```

into this:

```text
Kubernetes Job running a containerized Developer Agent with the right task envelope and runtime configuration.
```

---

# 2. Why This Component Exists

Agents must not be allowed to run freely without control.

The Agent Coordinator exists to ensure:

- every agent task runs in an isolated container
- every task has a structured payload
- every execution is traceable
- every worker has minimum necessary permissions
- every worker exits after the task
- every task result is structured
- secrets are injected only where needed
- failed jobs are visible and recoverable

Without the Agent Coordinator, the system becomes an uncontrolled collection of containers.

---

# 3. Position in the Architecture

```text
Human
  -> Orchestrator
  -> Agent Coordinator
  -> Kubernetes Job
  -> Agent Worker Container
  -> GitHub / Repo / Tests
  -> Structured Result
  -> Orchestrator
```

The Agent Coordinator sits between:

```yaml
upstream:
  - orchestrator

downstream:
  - kubernetes
  - docker
  - agent_worker_containers
  - openclaw_runtime
```

---

# 4. Runtime Model

The system uses two runtime types.

## 4.1 Long-running services

These are Kubernetes Deployments:

```yaml
long_running_services:
  - orchestrator
  - github_integration
  - agent_coordinator
  - postgres
```

## 4.2 Short-lived execution workers

These are Kubernetes Jobs:

```yaml
short_lived_workers:
  - advisor_worker
  - idea_consultant_worker
  - product_manager_worker
  - developer_worker
  - tester_worker
  - reviewer_worker
```

The Agent Coordinator launches short-lived Jobs.

---

# 5. Input Contract

The Agent Coordinator receives a dispatch request.

Example:

```json
{
  "initiative_id": "INIT-001",
  "task_id": "TASK-001",
  "role": "developer",
  "specialization": "backend",
  "repo": "your-org/your-repo",
  "instructions": [
    "Implement project creation endpoint",
    "Add validation",
    "Add tests"
  ],
  "metadata": {
    "base_branch": "main",
    "working_branch": "agent/developer/task-001",
    "owner_agent_id": "AGENT-DEV-BACKEND-1",
    "risk_level": "medium",
    "lane": "fast_lane"
  }
}
```

The Agent Coordinator must validate:

```yaml
required_fields:
  - initiative_id
  - task_id
  - role

optional_but_recommended:
  - specialization
  - repo
  - instructions
  - base_branch
  - working_branch
```

If required fields are missing, reject the request.

---

# 6. Worker Envelope

The Agent Coordinator transforms the dispatch request into a Worker Task Envelope.

Example:

```json
{
  "initiative_id": "INIT-001",
  "task_id": "TASK-001",
  "role": "developer",
  "specialization": "backend",
  "repo": "your-org/your-repo",
  "base_branch": "main",
  "working_branch": "agent/developer/task-001",
  "inputs": {
    "instructions": [
      "Implement project creation endpoint",
      "Add validation",
      "Add tests"
    ],
    "owner_agent_id": "AGENT-DEV-BACKEND-1",
    "risk_level": "medium",
    "lane": "fast_lane",
    "profile": {
      "mode": "implementation",
      "image": "agent-platform/base-worker:dev"
    }
  }
}
```

The envelope must be passed to the worker through:

```bash
TASK_ENVELOPE_JSON=<json>
```

---

# 7. Runtime Profiles

The Agent Coordinator must map agent role and specialization to runtime profile.

## Default profile map

```yaml
runtime_profiles:
  advisor:
    image: agent-platform/base-worker:dev
    mode: analysis
    repo_access: read_only
    can_write_code: false

  idea_consultant:
    image: agent-platform/base-worker:dev
    mode: concept_refinement
    repo_access: read_only
    can_write_code: false

  product_manager:
    image: agent-platform/base-worker:dev
    mode: planning
    repo_access: read_only
    can_write_code: false

  developer:
    image: agent-platform/base-worker:dev
    mode: implementation
    repo_access: read_write
    can_write_code: true

  tester:
    image: agent-platform/base-worker:dev
    mode: validation
    repo_access: read_only
    can_write_code: false
    can_write_tests: false_by_default

  reviewer:
    image: agent-platform/base-worker:dev
    mode: review
    repo_access: read_only
    can_write_code: false
```

## Specialization override example

```yaml
developer.backend:
  image: agent-platform/base-worker:dev
  mode: backend_implementation
  allowed_paths:
    - apps/
    - packages/
    - tests/

developer.devops:
  image: agent-platform/base-worker:dev
  mode: infra_implementation
  allowed_paths:
    - infra/
    - .github/
    - Dockerfile
    - docker-compose.yml

tester.e2e:
  image: agent-platform/base-worker:dev
  mode: e2e_validation
  allowed_paths:
    - tests/
    - e2e/
    - playwright/
    - cypress/

reviewer.security:
  image: agent-platform/base-worker:dev
  mode: security_review
  repo_access: read_only
```

---

# 8. Kubernetes Job Requirements

Every launched agent task should run as a Kubernetes Job.

## Required metadata

```yaml
metadata:
  labels:
    app: agent-worker
    task_id: TASK-001
    role: developer
    specialization: backend
    initiative_id: INIT-001
```

## Required Job settings

```yaml
job:
  restartPolicy: Never
  backoffLimit: 0
  ttlSecondsAfterFinished: 3600
```

## Required container env

```yaml
env:
  - TASK_ENVELOPE_JSON
  - OPENCLAW_PROVIDER
  - OPENCLAW_AUTH_MODE
  - OPENCLAW_CONFIG_PATH
  - OPENCLAW_WORKSPACE_ROOT
  - DEFAULT_REPO
  - DEFAULT_BASE_BRANCH
```

## Recommended resource limits

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "512Mi"
  limits:
    cpu: "2"
    memory: "4Gi"
```

Developer and tester jobs may need higher limits depending on repo size.

---

# 9. Docker Runtime Fallback

For local development, the Agent Coordinator may support Docker directly.

This is optional.

Docker fallback is useful when:

- k3s is not installed
- local debugging is needed
- worker behavior is being developed

Docker command shape:

```bash
docker run --rm \
  -e TASK_ENVELOPE_JSON="$TASK_ENVELOPE_JSON" \
  -e OPENCLAW_PROVIDER="$OPENCLAW_PROVIDER" \
  -v "$PWD/workspaces:/workspace" \
  agent-platform/base-worker:dev
```

Kubernetes remains the preferred execution mode.

---

# 10. OpenClaw Runtime Injection

The Agent Coordinator must inject OpenClaw-related environment values into worker Jobs.

Required placeholders:

```bash
OPENCLAW_PROVIDER=chatgpt_oauth
OPENCLAW_AUTH_MODE=manual_oauth
OPENCLAW_CONFIG_PATH=__REPLACE_WITH_LOCAL_OPENCLAW_CONFIG_PATH_IF_NEEDED__
OPENCLAW_WORKSPACE_ROOT=/workspace
OPENCLAW_SESSION_TOKEN=__REPLACE_IF_YOUR_RUNTIME_EXPORTS_ONE__
OPENCLAW_PROFILE_NAME=__REPLACE_IF_NEEDED__
OPENCLAW_MODEL_NAME=__REPLACE_IF_NEEDED__
```

The human operator must complete OAuth manually before live execution.

The Agent Coordinator must never log:

- OAuth tokens
- session tokens
- private keys
- GitHub App private keys
- repository credentials

---

# 11. Workspace Policy

Each worker should get an isolated workspace.

Recommended pattern:

```text
/workspace/<initiative-id>/<task-id>
```

Example:

```text
/workspace/INIT-001/TASK-001
```

## Workspace rules

```yaml
workspace_rules:
  - no shared writable workspace between unrelated tasks
  - no cross-task mutation
  - preserve artifacts after job if configured
  - delete temporary files after completion if safe
```

---

# 12. Result Contract

Each worker must emit a structured result.

Example:

```json
{
  "task_id": "TASK-001",
  "status": "pr_opened",
  "branch": "agent/developer/task-001",
  "pr_number": 42,
  "summary": "Implemented endpoint and tests.",
  "artifacts": [
    "/workspace/INIT-001/TASK-001/test-results.txt"
  ]
}
```

The Agent Coordinator must collect or observe this result and send it back to the Orchestrator.

For v1, acceptable result collection methods:

```yaml
result_collection_methods:
  - worker prints JSON to stdout
  - worker writes result.json to mounted artifact path
  - worker posts result to orchestrator callback URL
```

Recommended v1:

```text
worker posts result to orchestrator callback URL
```

Local fallback:

```text
worker prints JSON to stdout
```

---

# 13. Worker Statuses

The Agent Coordinator should track these statuses:

```yaml
worker_statuses:
  - queued
  - launched
  - running
  - succeeded
  - failed
  - timed_out
  - cancelled
  - unknown
```

The Orchestrator-facing task state is separate from Kubernetes worker state.

Example:

```yaml
task_status: implementation_in_progress
worker_status: running
```

---

# 14. Failure Handling

The Agent Coordinator must detect:

```yaml
failure_conditions:
  - job_creation_failed
  - image_pull_failed
  - pod_crash_loop
  - worker_exit_nonzero
  - timeout
  - missing_result
  - invalid_result_schema
  - credentials_missing
  - openclaw_auth_missing
```

Failure response format:

```json
{
  "task_id": "TASK-001",
  "worker_status": "failed",
  "failure_type": "openclaw_auth_missing",
  "message": "OpenClaw OAuth config was not found in the expected path.",
  "next_recommended_step": "human"
}
```

---

# 15. Timeout Policy

Each role should have a timeout.

Recommended defaults:

```yaml
timeouts:
  advisor: 10m
  idea_consultant: 15m
  product_manager: 20m
  developer: 60m
  tester: 45m
  reviewer: 30m
```

If a task times out:

1. mark worker as timed_out
2. preserve logs
3. notify Orchestrator
4. route to human or retry depending on policy

Retry should be conservative.

---

# 16. Retry Policy

Default retry policy:

```yaml
retry_policy:
  advisor: 1
  idea_consultant: 1
  product_manager: 1
  developer: 0
  tester: 1
  reviewer: 1
```

Developer retries should be manual by default to avoid repeated uncontrolled code changes.

---

# 17. Runtime Security

The Agent Coordinator must apply least privilege.

## Default pod security

```yaml
security_context:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

## Network policy recommendation

```yaml
network:
  allow_to_github: true
  allow_to_orchestrator: true
  allow_to_package_registries: true
  deny_unneeded_internal_services: true
```

## Secret policy

```yaml
secret_policy:
  inject_only_required_secrets: true
  never_log_secrets: true
  rotate_when_compromised: true
```

---

# 18. Runtime Permissions by Role

```yaml
permissions:
  advisor:
    repo: read
    github_write: false

  idea_consultant:
    repo: read
    github_write: false

  product_manager:
    repo: read
    issues_write: optional

  developer:
    repo: write_branch_only
    pull_request_write: true
    merge: false

  tester:
    repo: read
    test_write: optional
    merge: false

  reviewer:
    repo: read
    review_comment_write: true
    merge: false
```

---

# 19. Agent Creation

The Agent Coordinator does not decide product-level need for agents.

It creates runtime capacity when instructed by the Orchestrator.

## Create runtime worker profile

Example:

```json
{
  "role": "developer",
  "specialization": "backend",
  "image": "agent-platform/base-worker:dev",
  "mode": "backend_implementation",
  "resource_profile": "standard",
  "timeout": "60m"
}
```

Codex should represent profiles in a config file such as:

```text
apps/agent-coordinator/app/profiles.py
```

or:

```text
configs/runtime-profiles.yaml
```

---

# 20. Agent Scaling

The Agent Coordinator supports scaling by:

1. launching more Jobs
2. selecting different runtime profiles
3. using Kubernetes Deployment replicas for long-running coordinators

## Worker scaling rule

Workers are not long-running replicas.  
They are per-task Jobs.

To increase throughput:

```yaml
scale_by:
  - allowing more concurrent jobs
  - registering more agents
  - increasing coordinator capacity
```

## Concurrency limits

Recommended local defaults:

```yaml
concurrency_limits:
  total_workers: 3
  developer_workers: 1
  tester_workers: 1
  reviewer_workers: 1
```

Because this system initially runs on one Ubuntu PC.

---

# 21. Agent Deletion / Disable Runtime

The Agent Coordinator must support safe disable semantics.

## Disable runtime profile

Example:

```yaml
runtime_profile:
  role: developer
  specialization: backend
  enabled: false
```

If disabled:

- do not launch new Jobs for this profile
- allow existing Jobs to finish
- report profile unavailable to Orchestrator

## Delete runtime artifacts

Safe deletion requires:

```yaml
delete_requirements:
  - no running jobs for profile
  - no active task assignments
  - logs preserved or explicitly discarded
  - artifacts preserved or explicitly discarded
```

---

# 22. Observability

The Agent Coordinator must expose or log:

```yaml
observability:
  - task_id
  - initiative_id
  - role
  - specialization
  - job_name
  - worker_status
  - start_time
  - finish_time
  - exit_code
  - failure_reason
```

For local deployment, logs can be inspected with:

```bash
kubectl -n agent-jobs get jobs
kubectl -n agent-jobs get pods
kubectl -n agent-jobs logs <pod-name>
```

---

# 23. API Contract

The Agent Coordinator should expose these endpoints.

## Health

```http
GET /healthz
```

Response:

```json
{
  "status": "ok"
}
```

## Launch task

```http
POST /tasks
```

Request:

```json
{
  "initiative_id": "INIT-001",
  "task_id": "TASK-001",
  "role": "developer",
  "specialization": "backend",
  "repo": "your-org/your-repo",
  "instructions": ["Implement feature"],
  "metadata": {
    "base_branch": "main",
    "working_branch": "agent/developer/task-001"
  }
}
```

Response:

```json
{
  "accepted": true,
  "coordinator": "default",
  "message": "Execution job launched: developer-task-001"
}
```

## Optional list jobs

```http
GET /jobs
```

Response:

```json
{
  "jobs": []
}
```

---

# 24. Kubernetes RBAC

The Agent Coordinator requires permission to create Jobs in the `agent-jobs` namespace.

Required RBAC:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: agent-coordinator
  namespace: agent-coordinators
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: agent-job-manager
  namespace: agent-jobs
rules:
  - apiGroups: ["batch"]
    resources: ["jobs"]
    verbs: ["create", "get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

---

# 25. Local Ubuntu 24.04 Requirements

The Agent Coordinator local runtime assumes:

```yaml
host:
  os: Ubuntu 24.04
  docker: installed
  k3s: installed
  kubectl: configured
  local_images_imported_to_k3s: true
```

Required local image tags:

```yaml
images:
  - agent-platform/orchestrator:dev
  - agent-platform/github-integration:dev
  - agent-platform/agent-coordinator:dev
  - agent-platform/base-worker:dev
```

---

# 26. Codex Implementation Instructions

When Codex is asked to implement the Agent Coordinator setup, it should:

1. create this markdown file under:

```text
runtime/coordinator/agent-coordinator.md
```

2. ensure the coordinator service exists under:

```text
apps/agent-coordinator/
```

3. implement endpoint:

```text
POST /tasks
```

4. implement Kubernetes Job launcher
5. pass `TASK_ENVELOPE_JSON` into each worker
6. map role/specialization to runtime profile
7. inject OpenClaw placeholders from environment or Kubernetes Secret
8. create RBAC for launching Jobs
9. support local fallback when kubeconfig is unavailable
10. never log secrets
11. preserve task ID and role in Job labels
12. return launch result to Orchestrator
13. expose health endpoint
14. document local debugging commands

---

# 27. Acceptance Criteria

This Agent Coordinator definition is complete when:

- Orchestrator can call coordinator
- Coordinator accepts structured task requests
- Coordinator maps role to runtime profile
- Coordinator creates Kubernetes Job
- Worker receives `TASK_ENVELOPE_JSON`
- OpenClaw env placeholders are injected
- Job labels include task, role, and initiative
- Coordinator uses least-privilege RBAC
- Coordinator does not leak secrets
- Coordinator supports local Ubuntu/k3s deployment
- behavior is documented in this file

---

# 28. Minimal Examples

## Launch developer task

```bash
curl -X POST http://127.0.0.1:8002/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "initiative_id": "INIT-001",
    "task_id": "TASK-001",
    "role": "developer",
    "specialization": "backend",
    "repo": "your-org/your-repo",
    "instructions": [
      "Implement project creation endpoint"
    ],
    "metadata": {
      "base_branch": "main",
      "working_branch": "agent/developer/task-001"
    }
  }'
```

## Inspect Jobs

```bash
kubectl -n agent-jobs get jobs
kubectl -n agent-jobs get pods
```

## Inspect logs

```bash
kubectl -n agent-jobs logs <pod-name>
```

---

# 29. Operating Principle

The Agent Coordinator must behave like a reliable local runtime manager:

```text
launch isolated work
inject only what is needed
track every execution
never leak secrets
keep local iteration fast
```
