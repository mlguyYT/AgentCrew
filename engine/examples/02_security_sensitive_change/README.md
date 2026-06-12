# Scenario 02 — Security-sensitive auth change

A request to touch `src/auth/middleware.py`. The project's
`.agentcrew/config.yaml` says: any change matching `src/auth/**` requires
a Security Reviewer. The classifier also flags the request as high-risk
(security trigger), so the workflow is Full Lane with Security Reviewer
attached as a specialist.

## Setup

```bash
cd examples/02_security_sensitive_change
cat .agentcrew/config.yaml
cat src/auth/middleware.py
cat task.txt
```

## What the classifier + project config produce (no API key)

```bash
agentcrew route --task "$(cat task.txt)" --project .
```

Expected output (excerpt):

```text
- lane: Full Lane
- quality profile: strict        ← from .agentcrew/config.yaml
- recipe: bug-fix
- next roles: Idea Consultant, Product Manager, Developer, Tester, Reviewer, Human

## Specialists
- Security Reviewer              ← required by config (paths: src/auth/**)
- Researcher Agent
```

The Security Reviewer being attached is the point of this scenario: even
without the security trigger in the request text, the project config
would add it on any file matching `src/auth/**`.

## Run end-to-end with a real backend

The bundled `mock-demo` backend is scripted only for the Developer →
Tester path used in scenario 01. To run scenario 02 through real LLM
calls (Advisor, PM, Developer, Tester, Reviewer, Security Reviewer), use
one of these backends. The cost gate previews the bill before any token
is spent.

### OpenAI-compatible endpoint

```bash
export OPENAI_API_KEY=...
agentcrew run --task "$(cat task.txt)" --project . --backend openai
```

Models can default from `.agentcrew/config.yaml`. Override per-role with
`--developer-model …`, `--security-reviewer-model …`, etc.

### Local (Ollama)

```bash
ollama pull qwen2.5-coder:14b
agentcrew run --task "$(cat task.txt)" --project . --backend local \
              --advisor-model qwen2.5-coder:14b \
              --product-manager-model qwen2.5-coder:14b \
              --developer-model qwen2.5-coder:14b \
              --tester-model qwen2.5-coder:14b \
              --reviewer-model qwen2.5-coder:14b \
              --security-reviewer-model qwen2.5-coder:14b
```

## What you should see

- Cost gate shows the per-role bill and the daily budget remaining.
- `.agent-state/runs/<id>/` contains one handoff JSON per role plus
  `task-routing.json`, `cost-estimate.json`, and `cost-actual.json`.
- Security Reviewer's handoff lists the timing-safe fix as evidence.
- Final decision: `ready_for_human_approval`.
- `agentcrew show --project .` renders a one-screen summary.
