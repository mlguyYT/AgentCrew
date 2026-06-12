# AgentCrew Engine

> **The methodology is the spec. The engine executes it with provider-neutral backends.**
>
> The engine reads role files from `agent-team/`, calls the classifier,
> follows the workflow string, and writes artifacts using the schemas
> defined in `agent-team/protocols/`. It owns no roles, no classification
> logic, no handoff format of its own. It's the bridge between the
> Markdown spec and an LLM provider.

## What this means in practice

When a user asks the engine to run a task, this is what happens:

1. The engine calls **`agent-team/tools/classify-task.sh`**. The classifier
   emits intent, risk, lane, quality profile, recipe, starting role,
   workflow, reviewers, specialists, skills, gates, and human decisions.
2. The engine writes **`.agent-state/current-task.md` and
   `task-routing.md`** using `agent-team/protocols/state-artifacts.md`
   and `agent-team/templates/task-routing.md` shapes.
3. The engine (optionally) **asks you to approve the routing** before
   any role runs. If the classifier returned `Direct Answer Mode`, no
   role runs — the engine surfaces the routing and exits.
4. For each role in the workflow (e.g. Developer → Tester):
   - The engine loads the role's system prompt from
     **`agent-team/agents/<slug>.md`** (read at runtime — not a copy).
   - The engine binds **the role-specific tool allowlist** (Developer
     can write; Tester is read+test-runner only; Reviewer is read-only;
     etc.).
   - The engine calls the LLM, the role acts, then **submits a Handoff**
     that the engine validates against
     `agent-team/protocols/handoff-format.md`.
   - The engine persists the Handoff to `.agent-state/handoff.md` AND
     the per-role report file (e.g. `test-report.md`,
     `security-review-report.md`) per
     `agent-team/protocols/state-artifacts.md`.
5. The engine stops on the first human-gate decision or after the
   workflow completes.

There is **no separate engine planner**, **no engine classification
logic**, **no parallel role registry**. The methodology owns all of
those.

## Where things live

| Concept | Where it lives |
|---|---|
| Roles (Developer, Tester, Reviewer, Security Reviewer, UX/Design Reviewer, Documentation Agent, Support Triage Agent, Release Manager, Researcher Agent, LLM Agent, CNN Agent, Skill Validator, Advisor, Idea Consultant, Product Manager) | `agent-team/agents/*.md` — read at runtime |
| Routing (intent, risk, lane, quality profile, recipe, workflow, gates, specialists) | `agent-team/tools/classify-task.sh` — shelled out by `routing.py` |
| Handoff schema | `agent-team/protocols/handoff-format.md` + `templates/compact-handoff.md` — Pydantic mirror in `handoff.py` |
| State artifact layout | `agent-team/protocols/state-artifacts.md` — implemented in `state.py` |
| Lane / quality profile / recipe semantics | `agent-team/{playbooks,quality-profiles,recipes}/` — referenced via the classifier's `files_to_load` |

If the methodology changes its schema, the engine's Pydantic + state
layer move with it. That's the right coupling.

## Quick start

```bash
cd engine
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

pytest -q                       # all tests should pass

# Verify the methodology link (defaults to sibling check; engine/ sits
# under the AgentCrew root)
agentcrew-engine doctor

# Preview what the classifier would do (no execution)
agentcrew-engine route --task "Refactor auth/middleware.py to OIDC"

# Run the bundled mock demo (uses the real classifier + scripted LLM
# responses)
rm -rf examples/01_python_bug_fix/.agent-state
agentcrew-engine run \
  --task "Fix broken.py so add_numbers returns a + b" \
  --project examples/01_python_bug_fix \
  --backend mock-demo \
  --auto-approve-routing
```

The mock-demo backend uses the **real classifier** to decide the
workflow, then runs scripted LLM responses for Developer + Tester. End
state lives in `.agent-state/` under the project and follows the
methodology's schema exactly.

> Most users invoke the engine through the top-level `bin/agentcrew run`
> wrapper, which forwards every argument to the engine. The
> `agentcrew-engine` binary is the underlying entry point.

## Backends

| Backend | Install | Where it talks to |
|---|---|---|
| `mock-demo` | base engine install | bundled scripted responses |
| `local` | `pip install -e ".[openai]"` | Ollama on localhost (probes on startup) |
| `openai` | `pip install -e ".[openai]"` | OpenAI / Together / Groq / OpenRouter / Mistral / DeepSeek / Anyscale / Fireworks / vLLM / LM Studio / llama.cpp server |
| `anthropic` | `pip install -e ".[anthropic]"` | optional provider-specific Messages API adapter |

`agentcrew-engine backends` lists them. `agentcrew-engine models` shows
recommended local models per role.

## Per-role model selection

```bash
export AGENTCREW_MODEL=qwen2.5-coder:14b                # fallback for every role
export AGENTCREW_REVIEWER_MODEL=llama3.3:70b            # override one
export AGENTCREW_SECURITY_REVIEWER_MODEL=qwen2.5:32b    # override another
```

Or via CLI flags: `--developer-model`, `--tester-model`,
`--security-reviewer-model`, `--ux-design-reviewer-model`,
`--documentation-agent-model`, etc. Slug = lowercase role name with `/`
and spaces replaced by `-`.

## Architecture

```
                  ┌─ User task ─┐
                  └──────┬──────┘
                         ▼
       ┌─ engine orchestrator ─────────────────────────────┐
       │                                                    │
       │  1. routing.classify(task)                         │
       │      └─▶ shells out to                              │
       │         agent-team/tools/classify-task.sh          │
       │                                                    │
       │  2. write current-task.md + task-routing.md        │
       │     (methodology schemas)                          │
       │                                                    │
       │  3. (optional) human gate on the routing           │
       │                                                    │
       │  4. for role in routing.acting_roles_in_order():   │
       │       agent = Agent(                               │
       │         role,                                      │
       │         role_file = agent-team/agents/...md,       │
       │         model     = caller-supplied                │
       │       )                                            │
       │       Provider.run_agent(                          │
       │         system_prompt = role file,                 │
       │         tools         = tools.build_tools(role),   │
       │         submit_tool   = submit_handoff schema      │
       │       )                                            │
       │       persist Handoff per                          │
       │       agent-team/protocols/state-artifacts.md      │
       │                                                    │
       │  5. stop on human-gate decision or completion      │
       └────────────────────────────────────────────────────┘
                         │
                         ▼
       ┌─ Provider plugin (lazy-loaded) ─┐
       │ mock-demo | local | openai | optional APIs │
       │  mock                            │
       └──────────────────────────────────┘
```

## File layout

```
engine/
├── agentcrew/
│   ├── agentcrew_root.py      # Resolves the AgentCrew root + role-slug mapping
│   ├── routing.py             # Shells classify-task.sh, parses to Routing dataclass
│   ├── handoff.py             # Pydantic mirror of handoff-format.md
│   ├── state.py               # Implements state-artifacts.md layout
│   ├── agents.py              # Agent dataclass — system prompt from role file
│   ├── tools.py               # Bounded tools, allowlist keyed on role names
│   ├── orchestrator.py        # Classifier-driven; no parallel planning logic
│   ├── provider.py            # Provider ABC + MockProvider
│   ├── provider_local.py      # Ollama-first local backend
│   ├── provider_openai.py     # Generic OpenAI-compatible HTTP
│   ├── provider_anthropic.py  # optional Anthropic backend
│   ├── cli.py                 # `agentcrew-engine` subcommands
│   └── demo_script.py         # Scripted LLM responses for the bundled example
├── tests/                     # uses the real classifier
├── examples/                  # runnable scenarios
└── pyproject.toml
```

**Notably absent:** `engine/roles/`. The engine owns no role markdown —
it reads them from `agent-team/` at runtime.

## CLI

```bash
agentcrew-engine doctor              # verify the methodology link works
agentcrew-engine route --task "..."  # preview what the classifier would route to
agentcrew-engine run --task "..." --project DIR --backend ...
agentcrew-engine backends            # list providers
agentcrew-engine models              # recommended local models per role
agentcrew-engine --help
```

## Pointing the engine at any AgentCrew install

By default the engine looks for the methodology as a sibling (`engine/`'s
parent). You can override:

```bash
export AGENTCREW_ROOT=/home/me/AgentCrew-fork
# or
agentcrew-engine run --agentcrew-root /home/me/AgentCrew-fork --task "..." ...
```

`--agentcrew-root` is a hard constraint: if the path doesn't look like a
valid install (missing `AGENTS.md`, `agent-team/`, `bin/agentcrew`, or
the classifier), the engine fails loudly. No silent fallback that could
mask a typo.

## Tests

```bash
pytest -q          # no API key, no LLM SDK required
```

Coverage highlights:

- `test_handoff.py` — Pydantic schema matches `protocols/handoff-format.md`
- `test_routing.py` — parser handles real classifier output, including
  quoted apostrophes, list `'none'` markers, and conditional workflow
  steps
- `test_agentcrew_root.py` — root resolution, role-slug mapping,
  explicit-path failure
- `test_tools.py` — sandbox boundaries; allowlist keyed on role names
- `test_orchestrator.py` — end-to-end with the real classifier + mock
  LLM: proves the classifier picks Developer→Tester for the demo task,
  both roles run, edit lands on disk, state artifacts match the
  methodology's schema

## What's intentionally not here yet

- **LLM-based routing refinement.** The classifier is deterministic and
  good enough for first cut. The Advisor is the only LLM call in the
  routing path today (and only for Direct Answer Mode).
- **Rework loops across specialists.** When a trailing specialist
  returns `needs_rework`, the engine surfaces it to the human rather
  than auto-looping back into the primary workflow.
- **Async provider I/O.** Trailing specialists are parallelized via
  threads, not asyncio. provider SDKs commonly support this pattern, but async providers would give better resource use under many concurrent runs.

## License

MIT. The engine is the executable layer; `agent-team/` is the
methodology. Both stay open, vendor-neutral, and Markdown-first.
