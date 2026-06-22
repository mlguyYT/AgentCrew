# Cloud Operations

## Purpose

Use this playbook for cost-bearing, externally deployed, or hard-to-forget resources.

Examples:

- managed model endpoints
- vector indexes or search endpoints
- cloud databases, queues, buckets, jobs, or services
- public demo deployments
- paid APIs or hosted eval runs

---

## Required Before Creating Or Updating Resources

- confirm the cost-bearing action with the human
- state what will be created or changed
- identify expected cost or cost driver when knowable
- record the stop condition or review window
- prepare the teardown command before creation when the platform supports it
- update `.agent-state/cloud-resources.md`

Use:

```text
agent-team/templates/cloud-resources.md
agent-team/checklists/cloud-operation.md
```

---

## During Work

Record:

- provider
- resource name or ID
- region or project when safe to record
- purpose
- creation time
- public endpoint or access boundary
- teardown command
- current status

Keep credentials, account identifiers that should stay private, raw customer data, and local auth commands out of shared artifacts.

---

## Required Before Stopping

- verify whether any paid or public resource remains active
- write the teardown command in `.agent-state/cloud-resources.md`
- warn the human if an endpoint or paid resource remains deployed
- record the next safe action

---

## Required After Teardown

- run the provider's verification command when available
- record deletion status and verification time
- remove stale endpoint references from handoff summaries
- keep only compact evidence needed by the next agent

