# Loader Management

## Purpose

AgentCrew is normally registered once outside target projects by writing small global loader blocks for supported coding agents.

Loader management lets users preview, install, inspect, and remove those loader blocks without copying AgentCrew into application repositories.

---

## Install Loaders

Install all supported loaders:

```bash
~/AgentCrew/bin/agentcrew install
```

Preview changes first:

```bash
~/AgentCrew/bin/agentcrew install --dry-run
```

Install one loader:

```bash
~/AgentCrew/bin/agentcrew install --agent codex
~/AgentCrew/bin/agentcrew install --agent claude
~/AgentCrew/bin/agentcrew install --agent openclaw
```

---

## Inspect Loaders

Use:

```bash
~/AgentCrew/bin/agentcrew status --project .
~/AgentCrew/bin/agentcrew doctor
```

`status` shows whether supported loaders are registered.

`doctor` checks whether loaders point to the current AgentCrew checkout and reports mismatches as warnings.

---

## Remove Loaders

Preview removal:

```bash
~/AgentCrew/bin/agentcrew uninstall --dry-run
```

Remove all AgentCrew-managed loader blocks:

```bash
~/AgentCrew/bin/agentcrew uninstall
```

Remove one loader:

```bash
~/AgentCrew/bin/agentcrew uninstall --agent codex
~/AgentCrew/bin/agentcrew uninstall --agent claude
~/AgentCrew/bin/agentcrew uninstall --agent openclaw
```

The uninstall command removes only the block between AgentCrew's managed markers. It leaves unrelated user instructions in the same file intact.

---

## Managed Markers

AgentCrew writes loader blocks between these markers:

```text
<!-- AgentCrew global loader: start -->
<!-- AgentCrew global loader: end -->
```

Do not manually edit inside the block unless you are intentionally overriding the generated loader. Re-run `agentcrew install` to refresh it.

---

## Target Projects

Loader management affects global agent instruction files only. It does not copy `AGENTS.md` or `agent-team/` into target projects and does not remove project code.
