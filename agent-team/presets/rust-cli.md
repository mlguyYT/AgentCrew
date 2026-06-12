# Rust CLI Preset

## Use When

Use for Rust command-line tools, system utilities, and stand-alone binaries.

## Default Skills

```text
rust-pro
shell-pro when scripting around the binary
```

## Architecture Focus

- keep argument parsing, business logic, and I/O separated
- use typed errors (anyhow / thiserror) — never panic on user-recoverable input
- preserve CLI flag and exit-code behavior unless behavior change is approved
- isolate filesystem and process boundaries for testability

## Validation Defaults

- cargo test --all-features
- cargo clippy -- -D warnings
- cargo fmt --check
- integration tests via assert_cmd when the binary is invoked end-to-end

## Review Gates

- behavior-preserving refactor check when public surface changes
- dependency and supply-chain gate when Cargo.toml or Cargo.lock changes
- compatibility rollout check when CLI flags or output format change

## Required Specialists Suggestion

- Security Reviewer when the CLI handles secrets, network egress, or shell-out
- Documentation Agent when CLI flags / help text change

## Config Defaults (suggested)

```yaml
quality_profile: strict
required_specialists:
  - paths: ["src/cli/**"]
    roles: ["Documentation Agent"]
```
