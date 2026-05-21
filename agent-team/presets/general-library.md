# General Library Preset

## Use When

Use for reusable packages, SDKs, shared modules, or libraries without a dominant app framework.

## Default Skills

Load language-specific Skills from `agent-team/skills/registry.md` based on source files and package metadata.

## Architecture Focus

- keep public API surface stable and documented
- isolate compatibility-sensitive behavior
- preserve data shapes, event names, schemas, and exported symbols unless behavior change is explicit
- favor small modules with clear contracts and low coupling

## Validation Defaults

- package test command when available
- type checking or compile command when configured
- coverage gate when coverage tooling exists
- compatibility tests for public API or serialization changes

## Review Gates

- Reviewer for public API, shared-module, or behavior-changing refactors
- Documentation Agent for README, examples, changelog, or public API behavior changes
- Security Reviewer for dependency, build, release, or supply-chain changes
