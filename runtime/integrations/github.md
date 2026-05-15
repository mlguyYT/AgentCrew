# GitHub Integration Agent / Service

## Purpose

The GitHub Integration Agent connects the multi-agent development system to GitHub.

It is responsible for:

1. creating issues
2. creating pull requests
3. updating pull requests
4. posting comments
5. reading PR status
6. reading CI/check status
7. receiving GitHub webhooks
8. mapping GitHub events to orchestrator workflow events
9. routing review comments and CI failures into rework loops

The GitHub Integration Agent must **not** decide product direction.  
It must **not** approve merge on behalf of the human.  
It must **not** bypass branch protection.  
It must **not** expose GitHub secrets or private keys.

---

# 1. Component Summary

## Component name

`github_integration`

## Alternative names

```yaml
aliases:
  - github_agent
  - github_gateway
  - scm_integration
  - pr_integration_service
```

## Primary responsibility

The GitHub Integration Agent translates between:

```text
internal workflow events
```

and:

```text
GitHub issues, pull requests, reviews, comments, checks, and webhooks
```

---

# 2. Position in Architecture

```text
Developer Agent
  -> Git branch / PR
  -> GitHub Integration
  -> Orchestrator
  -> Tester / Reviewer / Specialist Reviewer / Human
```

Webhook flow:

```text
GitHub webhook
  -> GitHub Integration
  -> normalized event
  -> Orchestrator
  -> workflow transition
```

---

# 3. Required GitHub App

Use a GitHub App, not personal access tokens, for the real system.

## Required placeholders

```bash
GITHUB_APP_ID=__REPLACE_WITH_GITHUB_APP_ID__
GITHUB_INSTALLATION_ID=__REPLACE_WITH_GITHUB_INSTALLATION_ID__
GITHUB_APP_PRIVATE_KEY=__REPLACE_WITH_GITHUB_APP_PRIVATE_KEY__
GITHUB_WEBHOOK_SECRET=__REPLACE_WITH_GITHUB_WEBHOOK_SECRET__
DEFAULT_REPO=__REPLACE_WITH_GITHUB_ORG_SLASH_REPO__
DEFAULT_BASE_BRANCH=main
```

## Required GitHub App permissions

```yaml
permissions:
  metadata: read
  contents: read_write
  pull_requests: read_write
  issues: read_write
  checks: read
```

## Recommended webhook events

```yaml
webhook_events:
  - pull_request
  - pull_request_review
  - pull_request_review_comment
  - issue_comment
  - check_run
  - check_suite
  - workflow_run
```

---

# 4. Security Requirements

The GitHub Integration Agent must never log:

- GitHub App private key
- installation access token
- webhook secret
- OAuth token
- OpenClaw token
- repo credentials

## Required controls

```yaml
security_controls:
  verify_webhook_signature: true
  use_installation_tokens: true
  avoid_personal_access_tokens: true
  avoid_admin_permissions: true
  no_branch_protection_bypass: true
```

---

# 5. Webhook Signature Verification

Every GitHub webhook must be verified using:

```http
X-Hub-Signature-256
```

Verification algorithm:

```text
expected = "sha256=" + HMAC_SHA256(webhook_secret, raw_body)
compare expected with received signature using constant-time comparison
```

If verification fails:

```yaml
response:
  status: 400
  reason: invalid_signature
```

---

# 6. Webhook Input Contract

GitHub sends raw webhooks.

The GitHub Integration Agent must normalize them into internal events.

Example normalized event:

```json
{
  "event_type": "pull_request_review",
  "action": "submitted",
  "repository": "your-org/your-repo",
  "delivery_id": "github-delivery-id",
  "payload": {
    "pull_request": {
      "number": 42
    },
    "review": {
      "state": "changes_requested"
    }
  }
}
```

---

# 7. Webhook Event Mapping

## Pull request opened

GitHub event:

```yaml
event: pull_request
action: opened
```

Internal meaning:

```yaml
workflow_event: pr.opened
next_possible_state: testing_in_progress
```

## Pull request synchronized

GitHub event:

```yaml
event: pull_request
action: synchronize
```

Internal meaning:

```yaml
workflow_event: pr.updated
next_possible_state: testing_in_progress
```

## Pull request closed and merged

GitHub event:

```yaml
event: pull_request
action: closed
merged: true
```

Internal meaning:

```yaml
workflow_event: pr.merged
next_state: merged
```

## Review changes requested

GitHub event:

```yaml
event: pull_request_review
review.state: changes_requested
```

Internal meaning:

```yaml
workflow_event: rework.requested
source: reviewer
route_to: original_developer_owner
```

## Review approved

GitHub event:

```yaml
event: pull_request_review
review.state: approved
```

Internal meaning:

```yaml
workflow_event: review.github_approved
note: does_not_replace_human_approval
```

## Check failure

GitHub event:

```yaml
event: check_run or check_suite
conclusion: failure
```

Internal meaning:

```yaml
workflow_event: rework.requested
source: ci
route_to: original_developer_owner
```

## Check success

GitHub event:

```yaml
event: check_run or check_suite
conclusion: success
```

Internal meaning:

```yaml
workflow_event: ci.passed
```

---

# 8. Pull Request Creation

Developer Agent or GitHub Integration may create PRs depending on implementation mode.

Recommended v1:

```yaml
pr_creation_owner: developer_worker
github_integration_role: helper_and_webhook_reader
```

Alternative:

```yaml
pr_creation_owner: github_integration
developer_worker_role: push_branch_only
```

Both are acceptable, but one must be chosen.

## Recommended startup choice

Use:

```yaml
developer_worker_creates_pr: true
```

because it is simpler and keeps the implementation flow direct.

GitHub Integration still tracks PRs and webhooks.

---

# 9. PR Body Template

When GitHub Integration creates or updates PRs, use this format:

```md
## Summary
<summary>

## Task
Task: `<task_id>`
Initiative: `<initiative_id>`

## Acceptance Criteria
- [ ] criterion 1
- [ ] criterion 2

## Tests
<commands and results>

## Agent Metadata
- Role: developer
- Specialization: backend
- Branch: agent/developer/task-001

## Human Approval
Required before merge.
```

---

# 10. PR Labels

Recommended labels:

```yaml
default_labels:
  - agent-generated
  - needs-test
  - needs-review
```

Role/specialization labels:

```yaml
specialization_labels:
  - backend
  - frontend
  - infra
  - security
  - e2e
```

Risk labels:

```yaml
risk_labels:
  - risk-low
  - risk-medium
  - risk-high
  - risk-critical
```

---

# 11. PR Ownership Tracking

Every PR must map back to:

```yaml
pr_work_item:
  initiative_id: string
  task_id: string
  repo: string
  pr_number: integer
  owner_agent_id: string
  tester_agent_id: string | null
  reviewer_agent_id: string | null
  status: string
  human_approval_state: pending | approved | changes_requested
```

The GitHub Integration Agent must not create untracked PRs.

---

# 12. Comment Handling

The GitHub Integration Agent must parse comments where relevant.

## Human change request

If human comments:

```text
/request-changes
```

or uses GitHub review changes requested, map to:

```yaml
workflow_event: human.changes_requested
route_to: developer_or_reviewer
```

## Reviewer change request

If reviewer submits changes requested:

```yaml
workflow_event: rework.requested
source: reviewer
route_to: original_developer_owner
```

## Tester failure

If Tester Agent comments with failure status:

```yaml
workflow_event: rework.requested
source: tester
route_to: original_developer_owner
```

---

# 13. CI Status Handling

GitHub Integration must read CI/check state.

## Required behavior

If CI fails:

```yaml
action:
  - create normalized event
  - notify orchestrator
  - request rework
  - route to original developer
```

If CI passes:

```yaml
action:
  - create normalized event
  - allow testing/review to continue
```

CI passing must not mean human approval.

---

# 14. Human Approval Boundary

The GitHub Integration Agent may observe human approval.

It must not create human approval.

## Allowed

```yaml
allowed:
  - read review state
  - read PR approvals
  - notify orchestrator
  - mark external signal observed
```

## Forbidden

```yaml
forbidden:
  - approve PR as human
  - merge PR
  - bypass required checks
  - dismiss required reviews
  - edit branch protection
```

Only human merges.

---

# 15. GitHub App Authentication

The real system should use installation tokens.

High-level flow:

```text
GitHub App private key
  -> signed JWT
  -> installation access token
  -> GitHub API request
```

Codex should implement the structure but keep placeholders until real values are provided.

Required files:

```text
packages/github/app_auth.py
packages/github/client.py
```

Required methods:

```python
class GitHubAppAuth:
    def is_configured(self) -> bool: ...
    def create_jwt(self) -> str: ...
    def get_installation_token(self) -> str: ...
```

If real key is unavailable, fail clearly:

```json
{
  "configured": false,
  "missing": ["GITHUB_APP_PRIVATE_KEY"]
}
```

---

# 16. API Contract

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

## GitHub webhook

```http
POST /webhooks/github
```

Headers:

```http
X-GitHub-Event: pull_request
X-Hub-Signature-256: sha256=...
```

Response:

```json
{
  "accepted": true,
  "event_type": "pull_request",
  "action": "opened"
}
```

## GitHub App status

```http
GET /auth/github-app/status
```

Response:

```json
{
  "configured": false
}
```

---

# 17. Orchestrator Integration

The GitHub Integration Agent must send normalized events to the Orchestrator.

Recommended endpoint:

```http
POST /integrations/events/github
```

Payload:

```json
{
  "event_type": "pull_request_review",
  "action": "submitted",
  "repository": "your-org/your-repo",
  "delivery_id": "abc-123",
  "payload": {
    "pull_request": {
      "number": 42
    },
    "review": {
      "state": "changes_requested"
    }
  }
}
```

---

# 18. Local Development

For local Ubuntu 24.04, webhooks may not reach localhost unless exposed.

Options:

```yaml
local_webhook_options:
  - ngrok
  - cloudflared tunnel
  - smee.io
  - manual webhook replay
```

Recommended for first local tests:

```yaml
first_local_test: manual_webhook_replay
```

Example manual replay:

```bash
curl -X POST http://127.0.0.1:8000/integrations/events/github \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "pull_request_review",
    "action": "submitted",
    "repository": "your-org/your-repo",
    "payload": {
      "pull_request": {"number": 42},
      "review": {"state": "changes_requested"}
    }
  }'
```

---

# 19. Error Handling

The GitHub Integration Agent must return clear errors.

Examples:

```yaml
errors:
  invalid_signature:
    status: 400
  missing_event_header:
    status: 400
  github_app_not_configured:
    status: 503
  repo_not_found:
    status: 404
  rate_limited:
    status: 429
  permission_denied:
    status: 403
```

Never hide a permission issue.

---

# 20. Observability

Log these fields:

```yaml
safe_logs:
  - event_type
  - action
  - repository
  - pr_number
  - mapped_workflow_event
  - task_id_if_found
  - status
```

Never log:

```yaml
forbidden_logs:
  - private_key
  - installation_token
  - webhook_secret
  - oauth_token
```

---

# 21. Deleting / Disabling GitHub Integration

The GitHub Integration Agent is a service, not a normal task agent.

## Safe disable procedure

1. disable inbound webhook route or stop service
2. preserve last processed delivery ID
3. stop dispatching webhook events
4. confirm no active PR events are being processed
5. remove deployment if needed

## Do not delete if:

- active PRs depend on webhook state
- pending CI failures have not been processed
- GitHub App credentials need rotation first

---

# 22. Codex Implementation Instructions

When Codex is asked to implement GitHub Integration, it should:

1. create this markdown file under:

```text
runtime/integrations/github.md
```

2. ensure service exists under:

```text
apps/github-integration/
```

3. implement:
   - `GET /healthz`
   - `POST /webhooks/github`
   - `GET /auth/github-app/status`
4. implement webhook signature verification
5. implement normalized GitHub event model
6. implement event forwarding to Orchestrator
7. implement PR review changes_requested mapping
8. implement CI failure mapping
9. implement GitHub App auth placeholders
10. ensure secrets are never logged
11. ensure no merge endpoint exists
12. document local webhook testing

---

# 23. Acceptance Criteria

This GitHub Integration definition is complete when:

- GitHub App placeholders are defined
- webhook secret verification is documented
- webhook endpoint exists
- normalized event model exists
- PR review change requests map to rework
- CI failures map to rework
- PR merge event maps to merged status
- human approval is not bypassed
- GitHub Integration cannot merge PRs
- local manual webhook replay is documented
- behavior is documented in this file

---

# 24. Minimal Examples

## Check health

```bash
curl http://127.0.0.1:8001/healthz
```

## Check GitHub App config status

```bash
curl http://127.0.0.1:8001/auth/github-app/status
```

## Send fake review webhook to Orchestrator

```bash
curl -X POST http://127.0.0.1:8000/integrations/events/github \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "pull_request_review",
    "action": "submitted",
    "repository": "your-org/your-repo",
    "payload": {
      "pull_request": {"number": 42},
      "review": {"state": "changes_requested"}
    }
  }'
```

---

# 25. Operating Principle

The GitHub Integration Agent must behave like a secure SCM gateway:

```text
verify every webhook
map events clearly
never merge
never leak secrets
keep GitHub as source of truth for PRs
```
