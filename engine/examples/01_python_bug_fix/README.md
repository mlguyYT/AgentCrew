# Scenario 01 — Python bug fix

Shows a one-line bug classified as Fast Lane, followed by Developer,
Tester, and human approval. The offline backend scripts the model
responses and makes no LLM calls.

For a fresh copy that leaves this example unchanged, run from any directory:

```bash
~/AgentCrew/bin/agentcrew demo
```

## Setup

```bash
cd examples/01_python_bug_fix
cat broken.py              # bug: returns a - b
cat task.txt
```

## What the classifier picks

```bash
agentcrew route --task "$(cat task.txt)" --project .
```

Expected output (excerpt):
```
- lane: Fast Lane
- starting role: Developer
- quality profile: standard
- recipe: bug-fix
- next roles: Tester, Human
- gates: tester validation
```

## Run end-to-end (no API key)

The command below modifies this fixture. Use `agentcrew demo` for a repeatable,
isolated run.

```bash
agentcrew run --task "$(cat task.txt)" --project . \
              --backend mock-demo --auto-approve-routing
agentcrew show --project .
```

Expected:
- `broken.py` is patched to `return a + b`
- Two handoffs: Developer → Tester, Tester → Human
- Final decision: `ready_for_human_approval`

## Run with a real model

```bash
# OpenAI-compatible endpoint
export OPENAI_API_KEY=...
agentcrew run --task "$(cat task.txt)" --project . --backend openai \
              --developer-model gpt-4o-mini --tester-model gpt-4o-mini

# Local Ollama
ollama pull qwen2.5-coder:7b
agentcrew run --task "$(cat task.txt)" --project . --backend local \
              --developer-model qwen2.5-coder:7b --tester-model qwen2.5-coder:7b
```
