# Dependency And Supply-Chain Gate

## Purpose

This playbook defines the default gate for dependency, lockfile, package manager, runtime, container, CI, and build-system changes.

These changes can affect security, deployability, reproducibility, and production behavior even when application code appears small.

---

## Triggers

Run this gate when any change touches:

```yaml
supply_chain_triggers:
  - dependency manifests
  - lockfiles
  - package manager configuration
  - language runtime versions
  - container images or Dockerfiles
  - CI workflows
  - build scripts
  - deployment scripts
  - package registry configuration
  - dependency overrides or resolutions
```

Examples include `package.json`, lockfiles, `requirements.txt`, `pyproject.toml`, `pom.xml`, `build.gradle`, `go.mod`, `Cargo.toml`, Dockerfiles, and CI YAML.

---

## Required Behavior

Agents should:

```yaml
supply_chain_checks:
  - run the ecosystem audit or security tool when available
  - inspect remaining vulnerable dependency paths
  - avoid forced or breaking audit fixes unless explicitly approved
  - document any override, resolution, pin, or ignore rule
  - rerun relevant tests after dependency updates
  - treat audit-clean-before-merge as the default gate for maintained projects
```

If audit tooling is unavailable, document that limitation and recommend the nearest project-standard equivalent.

---

## Human Approval Required

The human must approve:

- breaking dependency upgrades
- forced audit fixes
- ignored vulnerabilities
- insecure legacy compatibility
- registry or provenance changes
- unresolved supply-chain risk before merge

---

## Output

Record:

```yaml
supply_chain_report:
  - files changed
  - audit command and result
  - remaining issues
  - dependency paths for unresolved issues
  - override or resolution rationale
  - tests rerun after dependency changes
  - recommendation
```
