# Skill: Reviewer Pro

## Purpose

Use this skill for disciplined code, design, and pull request review.

This skill can be used by Reviewer agents, Developer agents doing self-review, and Tester agents checking whether validation evidence is enough for human approval.

---

## Applies when

Use this skill when work involves:

- pull request review
- merge request review
- code review
- design review for an implementation
- risk review
- maintainability review
- test adequacy review
- security-sensitive review routing
- reviewer feedback or rework requests

---

## Detection triggers

Load this skill if the task or repo contains:

```yaml
triggers:
  text:
    - reviewer
    - review
    - code review
    - pull request review
    - PR review
    - merge request review
    - MR review
    - maintainability
    - test adequacy
    - edge cases
    - approval readiness
    - rework request
  files:
    - "agent-team/templates/review-report.md"
    - ".github/PULL_REQUEST_TEMPLATE.md"
    - "CODEOWNERS"
    - ".github/CODEOWNERS"
```

---

## Instructions

When reviewing work:

- Start with the task objective, acceptance criteria, and changed files.
- Check whether the change solves the intended problem for users or maintainers.
- Inspect design, correctness, edge cases, complexity, tests, documentation, and operational risk.
- Look at enough surrounding code to understand the change in context.
- Ask for domain reviewers when the change touches areas outside the current reviewer's expertise, especially security, privacy, accessibility, database, infrastructure, or billing.
- Separate blocking findings from optional suggestions.
- Ground comments in evidence, not personal preference.
- Prefer small, actionable rework requests that route back to the Developer.
- Mention what was not reviewed if the review scope is partial.
- Do not approve as the human and do not merge.

---

## Testing guidance

Reviewer should check:

- which tests were run
- whether the tests match the changed behavior
- whether missing tests are justified
- whether tests would fail for the bug or regression being guarded against
- whether user-facing changes need manual verification or screenshots
- whether risky changes need specialist validation

Useful commands depend on the project. Prefer commands documented in:

```text
README.md
CONTRIBUTING.md
Makefile
package.json
pyproject.toml
pom.xml
build.gradle
.github/workflows
```

Only claim validation was run if it was actually run.

---

## Review checklist

Reviewer should check:

- task scope is respected
- behavior matches acceptance criteria
- implementation is understandable in the surrounding system
- complexity is justified by current requirements
- no unrelated refactors or formatting churn are mixed in
- edge cases and error paths are handled
- tests cover changed behavior and meaningful failure modes
- security, privacy, data, auth, billing, and infrastructure risks are identified
- documentation or migration notes are updated when user or operator behavior changes
- review findings include severity, affected files, and required changes

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - approving as the human
  - merging or bypassing branch protection
  - blocking on personal style preferences
  - nitpicking while missing correctness or risk
  - reviewing only the diff when surrounding context is needed
  - ignoring missing test evidence
  - asking the reviewer to rewrite the PR instead of routing rework to Developer
  - treating silence from specialists as approval
  - hiding uncertainty about partial review scope
  - expanding the PR beyond the original task during review
```

---

## Research basis

This skill is based on public code review guidance from:

- Google Engineering Practices: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- GitLab Code Review Guidelines: https://docs.gitlab.com/development/code_review/

---

## Output note

If relevant, include:

```md
## Skills Applied
- reviewer-pro
```
