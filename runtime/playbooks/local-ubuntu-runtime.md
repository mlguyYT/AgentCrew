# Local Ubuntu 24.04 Runtime Playbook

## Purpose

This document defines the local execution environment.

---

# 1. Target Host

```yaml
host:
  os: Ubuntu 24.04
  docker: required
  k3s: required
  kubectl: required
```

---

# 2. Services

Run as Kubernetes Deployments:

```yaml
services:
  - orchestrator
  - github_integration
  - agent_coordinator
  - postgres
```

Run as Kubernetes Jobs:

```yaml
jobs:
  - developer worker
  - tester worker
  - reviewer worker
  - pm worker
  - advisor worker
  - idea consultant worker
  - ci execution worker
```

---

# 3. Local Startup Order

```bash
bash scripts/01_install_prereqs.sh
bash scripts/02_install_docker.sh
bash scripts/03_install_k3s.sh
bash scripts/04_build_images.sh
bash scripts/05_import_images_into_k3s.sh
bash scripts/06_apply_secrets.sh
bash scripts/07_deploy_k8s.sh
bash scripts/08_port_forward.sh
```

---

# 4. Required Placeholders

```yaml
placeholders:
  - DEFAULT_REPO
  - GITHUB_APP_ID
  - GITHUB_INSTALLATION_ID
  - GITHUB_APP_PRIVATE_KEY
  - GITHUB_WEBHOOK_SECRET
  - OPENCLAW_CONFIG_PATH
  - POSTGRES_PASSWORD
```

---

# 5. OpenClaw Manual OAuth

The human must complete OpenClaw OAuth manually.

The system must treat OpenClaw credentials as externally supplied runtime config.

Do not log OpenClaw tokens.

---

# 6. Local Concurrency Defaults

```yaml
local_concurrency:
  total_workers: 3
  developer_workers: 1
  tester_workers: 1
  reviewer_workers: 1
  ci_workers: 1
```

The local PC should not be overloaded.

---

# 7. Health Checks

```bash
kubectl get pods -A
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8001/healthz
curl http://127.0.0.1:8002/healthz
```
