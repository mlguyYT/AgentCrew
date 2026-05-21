# Release Recipe

## Use For

Release readiness, changelog, version bump, PR preparation, default-branch merge readiness, and ship/deploy preparation.

## Default Route

```text
Tester -> Reviewer -> Documentation Agent when public notes change -> Human
```

## Agent Focus

- verify clean worktree and current branch context
- run appropriate validation before release recommendation
- update changelog or release notes when needed
- run dependency/supply-chain checks when package, lock, runtime, CI, container, or build files changed
- keep final merge and release approval human-only

## Required Playbooks

```text
agent-team/playbooks/default-branch-merge.md
agent-team/checklists/release-readiness.md
```
