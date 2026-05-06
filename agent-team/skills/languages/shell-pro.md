# Skill: Shell Pro

## Purpose

Use this skill for professional shell scripting, automation, CI helper scripts, and local developer tooling.

## Applies when

Use this skill when work involves:

- shell scripts
- Bash scripts
- CI command wrappers
- install or setup scripts
- POSIX command usage
- developer automation

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - shell
    - bash
    - script
    - CLI
  files:
    - "*.sh"
    - "scripts/**"
    - "Makefile"
    - ".github/workflows/*.yml"
  code_symbols:
    - "#!/usr/bin/env bash"
    - "set -e"
    - "set -euo pipefail"
```

## Developer instructions

- Prefer clear, portable commands unless Bash-specific behavior is needed.
- Quote variables.
- Use `set -euo pipefail` when appropriate for Bash scripts.
- Handle paths with spaces.
- Avoid destructive commands without explicit human approval.
- Keep scripts idempotent where practical.
- Do not print secrets.

## Testing guidance

Look for:

```bash
shellcheck scripts/*.sh
bash -n script.sh
make test
```

Run project-specific script tests when available.

## Review checklist

- variables are quoted
- error handling is intentional
- destructive actions are guarded
- secrets are not printed
- paths with spaces are considered
- CI behavior is documented if changed

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - unquoted variables
  - unsafe rm usage
  - curl pipe shell without human approval
  - printing environment secrets
  - relying on local-only paths without documenting them
```

## Output note

If relevant, include:

```md
## Skills Applied
- shell-pro
```
