# Security Policy

This project is a workflow and documentation system.

For the detailed security guide, see:

```text
docs/security.md
```

It should never encourage:

- committing secrets
- printing secrets
- bypassing branch protection
- approving as the human
- merging PRs automatically
- hiding failed tests
- making destructive production changes without explicit human approval

## Reporting security issues

If you find a security issue in the workflow, open a private security advisory if the repository supports it, or contact the maintainers through the project's preferred private channel.

## Recommended safeguards

Repositories using this workflow should enable:

- branch protection
- required pull request reviews
- required status checks where practical
- secret scanning
- dependency scanning
- CODEOWNERS for maintained areas

Security-sensitive work should use Full Lane and receive explicit human approval.
