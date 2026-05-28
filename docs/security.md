# Security Policy

## Security philosophy

This project is a workflow and documentation system.

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
