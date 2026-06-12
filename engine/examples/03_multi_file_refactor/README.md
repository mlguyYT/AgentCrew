# Scenario 03 — Multi-file refactor with parallel specialists

Extract a duplicated helper into its own module, update both call
sites, and keep the docs in sync. This triggers Full Lane (recipe
`refactor`) and — because the task touches `docs/api.md` — the project
config pulls in **Documentation Agent** alongside Reviewer.

## Setup

```bash
cd examples/03_multi_file_refactor
cat task.txt
cat .agentcrew/config.yaml
ls src/ docs/
```

## What the classifier + project config produce (no API key)

```bash
agentcrew route --task "$(cat task.txt)" --project .
```

Expected output (excerpt):

```text
- lane: Full Lane
- quality profile: strict
- recipe: refactor
- next roles: Idea Consultant, Product Manager, Developer, Tester, Reviewer, Human

## Specialists
- Security Reviewer              ← classifier: `auth.py` triggers security
- Documentation Agent            ← required by config (paths: docs/**)
```

## Trailing specialists run in parallel

After Developer / Tester / Reviewer finish, the trailing specialists
(Security Reviewer, Documentation Agent) run concurrently — they
don't depend on each other. Look at the `mtime`s of the
`<run-dir>/handoff-*.json` files after a run; the specialist handoffs
land within milliseconds of each other.

## Run end-to-end with a real backend

The bundled `mock-demo` backend is scripted only for the Developer →
Tester path used in scenario 01. To run scenario 03 through real LLM
calls, use a local model, an OpenAI-compatible endpoint, or another optional provider backend.

```bash
export OPENAI_API_KEY=...
agentcrew run --task "$(cat task.txt)" --project . --backend openai \
              --advisor-model gpt-4o-mini \
              --product-manager-model gpt-4o-mini \
              --developer-model gpt-4o-mini \
              --tester-model gpt-4o-mini \
              --reviewer-model gpt-4o-mini \
              --documentation-agent-model gpt-4o-mini \
              --security-reviewer-model gpt-4o
```

The cost gate previews the total bill before any token is spent.

## What you should see

- Cost gate shows the per-role bill and the daily budget remaining.
- `agentcrew show --project .` renders the routing, all handoffs, and
  the actual cost when the run finishes.
- Final decision: `ready_for_human_approval`.
- `src/email_utils.py` exists; `src/users.py` and `src/auth.py` both
  import it; `docs/api.md` references the new module.
