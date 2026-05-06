# Skill: Rust Pro

## Purpose

Use this skill for professional Rust development in services, libraries, CLIs, tests, and systems code.

## Applies when

Use this skill when work involves:

- Rust source files
- Cargo packages
- ownership and borrowing
- async Rust
- traits and generics
- Rust tests

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - Rust
    - Cargo
    - borrow checker
    - async Rust
  files:
    - "*.rs"
    - "Cargo.toml"
    - "Cargo.lock"
  code_symbols:
    - Result
    - Option
    - async fn
    - trait
    - impl
```

## Developer instructions

- Prefer clear ownership over clever lifetime gymnastics.
- Use `Result` and `Option` intentionally.
- Avoid `unwrap` and `expect` in recoverable paths.
- Keep trait abstractions justified.
- Preserve public crate API unless task requires change.
- Keep unsafe code out unless explicitly required and documented.

## Testing guidance

Look for:

```bash
cargo test
cargo check
cargo clippy -- -D warnings
cargo fmt --check
```

## Review checklist

- errors are handled intentionally
- ownership and lifetimes are understandable
- no unnecessary `unsafe`
- public API changes are documented
- tests cover changed behavior
- clippy/fmt expectations are respected

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - unwrap in recoverable paths
  - unsafe without documented invariants
  - overgeneric trait designs
  - cloning to avoid understanding ownership
  - broad Cargo dependency churn
```

## Output note

If relevant, include:

```md
## Skills Applied
- rust-pro
```
