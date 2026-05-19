# Definition of Done

## Purpose

This checklist defines when work can be considered complete.

It applies to both human and agent-assisted work.

---

## Minimum done criteria

A task is done when:

- [ ] the requested behavior is implemented
- [ ] acceptance criteria are addressed
- [ ] changes are focused and scoped
- [ ] implementation remains modular and aligned with clean architecture
- [ ] refactors preserve legacy behavior unless behavior change is explicit
- [ ] relevant tests are added or updated
- [ ] tests were run or limitations are documented
- [ ] integration-test need was evaluated when behavior spans modules or external systems
- [ ] coverage is at least 70 percent when coverage tooling exists, or the gap is documented for human decision
- [ ] PR description is clear
- [ ] known risks are documented
- [ ] no secrets are committed
- [ ] committed state is team-neutral and contains no personal identifiers, private paths, or workstation-specific auth commands
- [ ] reviewer concerns are addressed or documented
- [ ] human approval is received before merge

---

## Fast Lane done

For Fast Lane work:

- [ ] PR is small
- [ ] change is low risk
- [ ] Tester validated changed behavior
- [ ] Reviewer was used if risk became meaningful or medium-or-higher
- [ ] Product Manager was used if scope or product behavior changed
- [ ] Security Reviewer was used if security-sensitive behavior changed
- [ ] UX / Design Reviewer was used if user-facing UI/UX changed
- [ ] Documentation Agent was used if docs, examples, changelog, or release notes changed
- [ ] dependency/supply-chain gate was used if dependency, runtime, container, CI, or build-system files changed
- [ ] human approved

---

## Full Lane done

For Full Lane work:

- [ ] idea brief exists
- [ ] product plan exists
- [ ] task acceptance criteria are explicit
- [ ] Tester report exists
- [ ] Reviewer report exists
- [ ] specialist reviewer report exists if required
- [ ] high/critical findings are resolved
- [ ] compatibility rollout and default-branch merge risks are documented if applicable
- [ ] human approved final PR

---

## Not done if

Work is not done if:

- [ ] tests are failing without explanation
- [ ] acceptance criteria are missing
- [ ] unrelated changes are included
- [ ] risky behavior is undocumented
- [ ] PR is too large to review
- [ ] human approval is missing
