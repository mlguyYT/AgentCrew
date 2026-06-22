# Artifact Classification

## Purpose

Classify artifacts before writing, committing, publishing, or sharing them.

Use:

```text
.agent-state/artifact-map.md
agent-team/templates/artifact-map.md
```

---

## Classes

```yaml
artifact_classes:
  public_repo: safe and intended for the repository
  private_local_note: useful locally but not for the repository
  ignored_runtime_file: local state that should stay gitignored
  cloud_resource: externally created resource that needs ownership and teardown state
  temporary_log_output: short-lived output that should be summarized then deleted or ignored
```

---

## Rules

- specs, generated chunks, raw logs, and intermediate outputs are not public by default
- customer-sensitive or commercially sensitive strategy belongs outside public artifacts unless the human approves
- cloud resources must also appear in `.agent-state/cloud-resources.md`
- commit only artifacts classified as `public_repo`
- keep ignored runtime state in `.agent-state/` or project-specific ignored paths

When classification is unclear, record a human decision instead of guessing.

