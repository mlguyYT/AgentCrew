# Context Manifest

## Purpose

`agentcrew context` prints the smallest useful AgentCrew file set for the next phase of a request.

Use it when an agent or human wants to avoid loading the whole methodology before work starts.

---

## Run

```bash
~/AgentCrew/bin/agentcrew context "Fix the login validation bug"
```

For a specific project:

```bash
~/AgentCrew/bin/agentcrew context --project /path/to/project --task "Add OAuth login"
```

The command is read-only. It does not write `.agent-state/` files.

---

## Output

The command prints:

```yaml
context_manifest:
  load_now:
    - minimum files needed for the next phase
  load_later:
    - validation, review, gate, and specialist files to load only when reached
```

`load_now` is the hot path. `load_later` preserves quality gates without paying the token cost before they are needed.

---

## How Agents Should Use It

1. Read `AGENTS.md`, `agent-team/context/route-index.md`, and `agent-team/protocols/token-discipline.md`.
2. Use `agentcrew context` when route or load set would otherwise be broad.
3. Load only `load_now` files for the current phase.
4. Load `load_later` files only when that phase or gate is triggered.

Do not load docs, examples, `STRUCTURE.md`, all playbooks, all roles, or all Skills during normal target-project work.
