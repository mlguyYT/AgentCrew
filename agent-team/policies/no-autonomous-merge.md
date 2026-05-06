# Policy: No Autonomous Merge

## Rule

Agents must not merge pull requests by default.

---

## Why

Autonomous merge can cause:

- broken main branch
- unreviewed product changes
- hidden security risk
- poor accountability
- accidental production impact

---

## Allowed agent actions

Agents may:

- create branches
- prepare PRs
- update PRs
- comment on PRs
- review PRs
- recommend human approval

---

## Forbidden agent actions

Agents must not:

- merge PRs
- bypass required checks
- dismiss required reviews
- force-push protected branches
- change branch protection

---

## Exception

Any exception must be explicit, repository-specific, and approved by the human maintainers.
