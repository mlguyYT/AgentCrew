# Testing Checklist

## Purpose

This checklist helps Tester Agents validate changes consistently.

---

## Before testing

- [ ] Read the task
- [ ] Read acceptance criteria
- [ ] Inspect changed files
- [ ] Identify relevant test commands
- [ ] Identify coverage command if the project has coverage tooling
- [ ] Identify risk level
- [ ] Decide whether integration tests are needed using `agent-team/checklists/integration-test-escalation.md`

---

## Test command discovery

Look for:

```text
README.md
Makefile
package.json
pyproject.toml
pytest.ini
go.mod
pom.xml
build.gradle
.github/workflows
```

Coverage commands may appear in the same files or in CI configuration.

---

## Test execution

- [ ] Run focused tests first
- [ ] Run broader tests if risk requires it
- [ ] Run coverage command when available
- [ ] Run integration tests when behavior spans modules or external systems
- [ ] Confirm coverage is at least 70 percent when coverage tooling exists
- [ ] Capture command output
- [ ] Report pass/fail honestly
- [ ] Do not invent results

If coverage tooling does not exist, document that limitation and recommend adding it when the project has production code.

---

## Acceptance criteria validation

For each criterion:

- [ ] passed
- [ ] failed
- [ ] not tested
- [ ] unclear

---

## Failure report

If something fails, include:

```yaml
failure_report:
  - command
  - expected_behavior
  - actual_behavior
  - coverage_percent_if_available
  - reproduction_steps
  - suspected_area
  - recommendation
```

---

## Recommendation

Tester should choose one:

```yaml
recommendation:
  - pass
  - rework_required
  - blocked
  - inconclusive
```
