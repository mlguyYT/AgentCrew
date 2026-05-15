# Optional Runtime Layer

This folder contains advanced design material for running the Agent Team workflow through services, coordinators, containers, GitHub integrations, and worker jobs.

The runtime layer is not required to use Agent Team.

Use the runtime material when you want to build a managed local or hosted agent platform around the Markdown workflow.

## Contents

```text
runtime/
  agents/
    advanced runtime role profiles, including specialist reviewers
  coordinator/
    agent coordinator design
  integrations/
    GitHub integration design
  playbooks/
    runtime and implementation playbooks
```

## Boundary

Core reusable workflow:

```text
AGENTS.md
agent-team/
docs/
```

Optional runtime design:

```text
runtime/
```

Keep new Kubernetes, Docker, OpenClaw, GitHub App, orchestration, and service-level content in this folder unless it is needed by the core Markdown workflow.
