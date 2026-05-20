# Quality Profile Selection

## Purpose

Choose the right quality profile for the product context before deciding how much review, validation, evidence, and output detail is needed.

Quality profiles do not override AgentCrew safety rules. They tune default rigor.

---

## Profiles

```yaml
profiles:
  light:
    file: agent-team/quality-profiles/light.md
    use_for: solo builders, prototypes, docs-only updates, tiny low-risk fixes

  standard:
    file: agent-team/quality-profiles/standard.md
    use_for: maintained products, startup teams, normal production repositories

  strict:
    file: agent-team/quality-profiles/strict.md
    use_for: enterprise teams, high-impact areas, shared platforms, critical APIs, complex refactors

  regulated:
    file: agent-team/quality-profiles/regulated.md
    use_for: legal, compliance, privacy, safety, financial, contractual, or audit-required work
```

Default to `standard` unless the user or project context clearly indicates another profile.

---

## Product Builder Modes

```yaml
solo_builder:
  default_profile: light
  default_output: brief
  escalate_to: standard when product is maintained or users depend on it

startup_team:
  default_profile: standard
  default_output: normal
  escalate_to: strict for auth, billing, customer data, platform, or hard-to-rollback changes

enterprise_team:
  default_profile: strict
  default_output: audit
  escalate_to: regulated when formal compliance or audit evidence is required

regulated_team:
  default_profile: regulated
  default_output: audit
  escalate_to: human decision queue for risk acceptance or quality gate override
```

---

## Selection Signals

Choose a stricter profile when any of these are true:

```yaml
stricter_profile_signals:
  - production users depend on the behavior
  - public API or compatibility changes
  - auth, billing, customer data, permissions, secrets, or sensitive data
  - infrastructure, deployment, runtime, container, CI, build-system, dependency, or lockfile change
  - rollback is difficult
  - work spans teams, modules, services, databases, caches, queues, timers, filesystems, or distributed state
  - compliance, privacy, legal, safety, financial, or contractual evidence requirements
  - human requests stricter handling
```

Choose a lighter profile only when:

```yaml
lighter_profile_allowed_when:
  - work is docs-only, exploratory, or tiny and reversible
  - no user-visible or security-sensitive behavior changes
  - no dependency, runtime, CI, build, migration, or infrastructure changes
  - human explicitly prefers lightweight handling
```

---

## Output Rule

For non-trivial work, include the selected profile in the route summary:

```text
Quality profile: standard
Reason: maintained product with user-facing behavior change
```

For tiny work, omit the line unless the profile changes the handling.

---

## Human Decision Queue

If a task requires accepting risk below the selected profile's gate, record it in:

```text
.agent-state/human-decisions.md
```

Use `agent-team/playbooks/human-decision-queue.md`.
