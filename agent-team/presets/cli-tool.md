# CLI Tool Preset

## Use When

Use for command-line tools, developer utilities, scripts, package generators, or local automation.

## Default Skills

Load language-specific Skills from `agent-team/skills/registry.md`; include `shell-pro` for shell entrypoints and install scripts.

## Architecture Focus

- keep command parsing, command execution, and output formatting separated
- make dry-run and force semantics explicit for write operations
- avoid hiding failures behind successful-looking output
- keep output stable enough for humans and scripts when practical

## Validation Defaults

- command help output works
- shell syntax checks for shell scripts
- unit tests or smoke tests for command behavior
- dry-run path tested when available

## Review Gates

- Reviewer for destructive operations, filesystem writes, install behavior, or generated artifacts
- Security Reviewer for credentials, auth commands, shell execution, downloads, or supply-chain changes
- Documentation Agent for command reference and examples
