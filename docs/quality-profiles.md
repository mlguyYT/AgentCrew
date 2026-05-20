# Quality Profiles

## Purpose

Quality profiles let AgentCrew adapt its rigor to the product context without making users learn every playbook.

The default profile is `standard`.

---

## Profiles

| Profile | Use For | Default Output | Typical User |
| --- | --- | --- | --- |
| `light` | prototypes, solo work, docs-only updates, tiny fixes | brief | solo builder |
| `standard` | maintained products and startup teams | normal | product team |
| `strict` | enterprise products, critical flows, shared platforms | audit | enterprise team |
| `regulated` | compliance, privacy, safety, financial, contractual, or audit-heavy work | audit | regulated team |

---

## Product Builder Modes

```yaml
solo_builder:
  profile: light

startup_team:
  profile: standard

enterprise_team:
  profile: strict

regulated_team:
  profile: regulated
```

These modes are defaults, not hard boundaries. AgentCrew should escalate when the task risk requires it.

---

## Files

```text
agent-team/playbooks/quality-profile-selection.md
agent-team/quality-profiles/light.md
agent-team/quality-profiles/standard.md
agent-team/quality-profiles/strict.md
agent-team/quality-profiles/regulated.md
```

---

## How To Use

Most users do not need to mention a profile. AgentCrew should choose one from project context and task risk.

Users may override explicitly:

```text
Use strict profile for this refactor.
```

Agents should not use a lighter profile to bypass safety rules, required tests, human-only decisions, or repository instructions.
