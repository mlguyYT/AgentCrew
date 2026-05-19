# Default Branch Merge

## Purpose

This playbook defines the checks required before merging a feature, fix, or refactor branch into the repository default branch.

Agents may prepare and validate merge readiness.
Agents may not merge to the default branch unless the human explicitly performs or approves that action under the repository's normal rules.

---

## Default Branch Detection

Do not assume the default branch is `main` or `master`.

Detect it from remote metadata when available:

```bash
git remote set-head origin --auto
git symbolic-ref --short refs/remotes/origin/HEAD
```

If remote metadata is unavailable, ask the human or inspect repository hosting configuration.

---

## Required Checks

Before default-branch merge, verify:

```yaml
default_branch_merge_checklist:
  - default branch detected from remote metadata or confirmed by human
  - remote fetched using the project's approved auth method
  - worktree is clean before merge validation
  - merge base is known
  - fast-forward possibility is known
  - conflict risk is documented
  - full validation has run on the post-merge target state
  - security and dependency checks have run if package, lock, runtime, container, CI, or build files changed
  - remaining risks and follow-up work are recorded
  - human approval exists before merge
```

---

## Validation Sequence

Recommended sequence:

```text
detect default branch
  -> fetch remote
  -> verify clean worktree
  -> verify merge base
  -> check fast-forward possibility
  -> create or simulate target merge state
  -> run full validation
  -> run supply-chain checks if needed
  -> document risks and follow-ups
  -> human decides merge
```

Use:

```text
agent-team/playbooks/dependency-supply-chain.md
```

when dependency, runtime, container, CI, or build-system files changed.

---

## Human-Only Boundary

Only the human may:

- merge to the default branch
- force-push or rewrite shared history
- accept failed validation
- accept security, data-loss, migration, or production-risk tradeoffs

Agents may prepare the branch, reports, and recommended command sequence.
