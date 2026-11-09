# Security Policy

## Security philosophy

AgentCrew includes a Markdown workflow and an executable coordination engine.

It should never encourage:

- secret leakage
- autonomous merging
- branch protection bypass
- unsafe production changes
- hidden test failures

---

## Agent safety rules

Agents must not:

```yaml
forbidden:
  - commit secrets
  - print secrets
  - bypass branch protection
  - approve as human
  - merge PRs automatically
  - remove tests to hide failures
  - make destructive infrastructure changes without explicit human approval
```

---

## Reporting security issues

If you find a security issue in the workflow, open a private security advisory if available, or contact the maintainers.

---

## Engine execution boundary

Model-issued commands require Linux Bubblewrap and working user namespaces.
Isolation is checked before command-capable roles call a model, and unavailable
isolation stops the run. There is no unconfined fallback.

The command environment exposes read-only system runtimes, the selected
project, and private temporary storage. It excludes host home directories and
network access. Existing Git metadata and engine-owned configuration/state are
read-only; file tools also protect those paths and reject external symlinks.
Commands can modify ordinary project files, so review their resulting diff.

Host-side Git inspection disables text converters, external diff programs,
filesystem monitors, hooks, and repository filters rather than executing them.
Runtime-state roots and artifacts cannot be symbolic links or hard-linked
aliases, so an existing state path cannot redirect work into another project.

Human approval boundaries are tracked separately from acting roles. Specialist
rework must be resolved or returned to the human, and unrelated passing tests
cannot erase unresolved validation failures. Unknown model pricing requires
explicit cost approval; token-based accounting does not replace provider billing.
Approving a product decision does not approve a new cost preview. Unpriced
usage remains recorded as unresolved and prevents a configured daily cap from
being treated as verified. Paid engine advice also uses these budget controls.

The portable Markdown workflow uses its host agent's execution controls.
See [engine setup](../engine/README.md#quick-start) for isolation requirements.

---

## Supply-chain trust boundary

Once `agentcrew install` registers a global loader, the AgentCrew checkout it
points at (`AGENTS.md` and `agent-team/`) becomes the **policy file** that
every Claude Code, Codex, OpenClaw, and Hermes session loads on this machine.
Anyone who can write to that directory can change how every future agent
behaves: which roles are loaded, what playbooks they follow, which Skills are
trusted, what gates apply, and even what counts as "human approval required".

Treat the AgentCrew checkout the same way you treat:

```yaml
trust_level:
  - CI configuration files (.github/workflows, etc.)
  - SSH config (~/.ssh/config)
  - shell rc files (~/.bashrc, ~/.zshrc)
```

Practical guidance:

- Install AgentCrew under your own user account, in a directory only you can
  write to (`chmod 700 ~/AgentCrew` is reasonable).
- Treat `git pull` of an upstream AgentCrew checkout the same way you treat
  updating CI templates — review the diff before pulling, especially around
  `AGENTS.md`, `agent-team/protocols/`, `agent-team/agents/`, and any
  installer or tool under `bin/` or `agent-team/tools/`.
- If you fork AgentCrew, set CODEOWNERS or branch protection on the fork so
  only your team can land changes to policy files.
- The installer's loader files (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`,
  `~/.openclaw/workspace/AGENTS.md`, `~/.hermes/SOUL.md`) are written with
  mode `0600` from v0.1.0 onward; `agentcrew doctor` warns if existing files
  have been widened. Do not loosen these permissions.
- Hostile `HERMES_PROFILE` and `OPENCLAW_PROFILE` env values are rejected
  by the installer from v0.1.0 onward, but `HERMES_HOME` and
  `OPENCLAW_STATE_DIR` are documented escape hatches and remain unchecked —
  set them only to paths you control.

---

## Recommended project safeguards

When using this workflow, also configure:

```yaml
recommended:
  - branch protection
  - required reviews
  - required status checks
  - secret scanning
  - dependency scanning
  - CODEOWNERS
```

---

## Human approval

Security-sensitive work should always use Full Lane.

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Security Reviewer -> Human
```

Use:

```text
agent-team/agents/security-reviewer.md
agent-team/templates/security-review-report.md
agent-team/checklists/security.md
```
