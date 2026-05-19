# Shared Memory Refresh

## Purpose

Use this checklist before committing or updating shared project state, memory, or handoff artifacts.

Shared state must be team-neutral. It should preserve project knowledge, not local workstation details or personal credentials.

---

## Refresh Checklist

Before saving shared state, verify:

- [ ] current default branch is correct
- [ ] current HEAD is correct
- [ ] current validation baseline is current
- [ ] current open risks are current
- [ ] current next steps are current
- [ ] stale phase notes are removed
- [ ] personal/local setup is removed
- [ ] secrets, private paths, and local auth details are removed

---

## Allowed Shared Context

Shared memory may include:

- current branch and default branch
- architecture decisions
- validation baseline
- known risks
- remaining work
- project conventions
- team-approved commands
- follow-up items

---

## Forbidden Shared Context

Shared memory must not include:

- personal Git identity
- personal email addresses
- private key paths
- deploy-key paths
- local machine paths
- workstation-specific auth commands
- tokens or secrets
- raw customer data
- sensitive production data
- large logs

If the context is only useful on one person's machine, keep it in local private notes instead of committed shared state.
