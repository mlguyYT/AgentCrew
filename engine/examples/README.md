# AgentCrew Example Scenarios

These are real runnable scenarios that demonstrate AgentCrew's coverage
of common situations a startup team will hit. Each scenario:

- Lives in its own folder with a tiny project structure
- Has a `README.md` showing the exact command and expected output
- Lets you preview the full routing with `agentcrew route` (no API key
  needed) and run end-to-end against `--backend local`, `--backend
  openai`, or another optional provider backend
- Scenario 01 also runs end-to-end with `--backend mock-demo` since the
  bundled scripted demo covers the Developer → Tester path

| # | Scenario | Demonstrates |
|---|---|---|
| 01 | Python bug fix | Fast Lane bug-fix; Developer → Tester → human approval |
| 02 | Security-sensitive auth change | Full Lane, mid-workflow human gate, Security Reviewer auto-inserted by config |
| 03 | Multi-file refactor | Parallel trailing specialists; Reviewer + Documentation Agent run concurrently |

## How to run any scenario

```bash
cd engine && source .venv/bin/activate
cd examples/01_python_bug_fix
agentcrew route --task "$(cat task.txt)" --project .         # preview routing (no API key)
agentcrew run   --task "$(cat task.txt)" --project . \
                --backend mock-demo --auto-approve-routing   # end-to-end demo, scenario 01 only
agentcrew show  --project .
```

`agentcrew route` always uses **the real classifier** — the lane
selection, recipe choice, specialist routing, and config-driven gate
attachment are all real. The `mock-demo` backend scripts only the
Developer → Tester turns used in scenario 01; scenarios 02 and 03 need
a real backend for full execution but preview correctly via `route`.
