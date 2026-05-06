# Testing Checklist

## Purpose

This checklist helps Tester Agents validate changes consistently.

---

## Before testing

- [ ] Read the task
- [ ] Read acceptance criteria
- [ ] Inspect changed files
- [ ] Identify relevant test commands
- [ ] Identify risk level

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

---

## Test execution

- [ ] Run focused tests first
- [ ] Run broader tests if risk requires it
- [ ] Capture command output
- [ ] Report pass/fail honestly
- [ ] Do not invent results

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
