# Security Checklist

## Purpose

This checklist helps agents avoid common security mistakes.

Use this especially for Full Lane work.

---

## Secrets

- [ ] No API keys committed
- [ ] No tokens committed
- [ ] No private keys committed
- [ ] No credentials in logs
- [ ] No secrets in screenshots
- [ ] `.env` files are ignored unless intentionally templated

---

## Authentication and authorization

- [ ] Auth behavior is not weakened
- [ ] Permissions are not broadened unnecessarily
- [ ] Protected routes remain protected
- [ ] User identity assumptions are clear
- [ ] Access control tests exist for risky changes

---

## Input validation

- [ ] User input is validated
- [ ] Unsafe input is rejected
- [ ] Error responses do not leak sensitive details
- [ ] Injection risks are considered

---

## Data handling

- [ ] Sensitive data is not logged
- [ ] Personal data exposure is avoided
- [ ] Data deletion behavior is intentional
- [ ] Migration risks are documented

---

## Dependencies

- [ ] New dependencies are justified
- [ ] Dependency source is trusted
- [ ] Unused dependencies are avoided
- [ ] Lockfile changes are expected

---

## Escalation

Escalate to human or Security Reviewer if:

- [ ] auth changes
- [ ] permissions change
- [ ] payment logic changes
- [ ] customer data handling changes
- [ ] destructive operations are introduced
