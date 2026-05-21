# Release Recipe

## Use For

Release readiness, changelog, version bump, PR preparation, default-branch merge readiness, and ship/deploy preparation.

## Default Route

```text
Release Manager -> Tester/Reviewer/Documentation Agent if evidence is missing -> Human
```

## Agent Focus

- verify clean worktree and current branch context
- run appropriate validation before release recommendation
- update changelog or release notes when needed
- run dependency/supply-chain checks when package, lock, runtime, CI, container, or build files changed
- keep final merge and release approval human-only
- prepare `.agent-state/release-report.md` when release evidence should be summarized

## Required Playbooks

```text
agent-team/playbooks/default-branch-merge.md
agent-team/checklists/release-readiness.md
agent-team/playbooks/release-management.md
```
