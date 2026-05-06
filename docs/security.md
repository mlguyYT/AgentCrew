# Security Policy

## Security philosophy

This project is a workflow and documentation system.

It should never encourage:

- secret leakage
- autonomous merging
- branch protection bypass
- unsafe production changes
- hidden test failures

---

## Agent safety rules

Agents must not:

```yaml
forbidden:
  - commit secrets
  - print secrets
  - bypass branch protection
  - approve as human
  - merge PRs automatically
  - remove tests to hide failures
  - make destructive infrastructure changes without explicit human approval
```

---

## Reporting security issues

If you find a security issue in the workflow, open a private security advisory if available, or contact the maintainers.

---

## Recommended project safeguards

When using this workflow, also configure:

```yaml
recommended:
  - branch protection
  - required reviews
  - required status checks
  - secret scanning
  - dependency scanning
  - CODEOWNERS
```

---

## Human approval

Security-sensitive work should always use Full Lane.

```text
Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Security Reviewer -> Human
```
