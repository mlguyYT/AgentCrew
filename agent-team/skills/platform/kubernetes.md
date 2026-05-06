# Skill: Kubernetes

## Purpose

Use this skill for Kubernetes manifests, Helm charts, Kustomize overlays, deployments, services, ingress, config maps, secrets references, and local cluster configuration.

---

## Applies when

Use this skill when work involves:

- Kubernetes YAML
- Deployments
- Services
- Ingress
- ConfigMaps
- Secrets references
- RBAC
- Helm
- Kustomize
- local k3s/minikube/kind

---

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - Kubernetes
    - k8s
    - deployment
    - service
    - ingress
    - helm
    - kustomize
    - kubectl
    - k3s
  files:
    - "k8s/**"
    - "infra/k8s/**"
    - "deployment.yaml"
    - "service.yaml"
    - "ingress.yaml"
    - "kustomization.yaml"
    - "Chart.yaml"
    - "values.yaml"
```

---

## Developer instructions

When modifying Kubernetes config:

- Keep manifests minimal and readable.
- Avoid hardcoding secrets.
- Use ConfigMaps/Secrets references appropriately.
- Preserve namespace conventions.
- Use labels consistently.
- Avoid broad changes across unrelated manifests.
- Be careful with destructive operations.
- Document manual steps if needed.
- Prefer local-safe defaults for development configs.

---

## Safety rules

Never introduce:

```yaml
forbidden:
  - plaintext production secrets
  - cluster-admin permissions without explicit need
  - destructive delete operations
  - privileged containers without explicit justification
  - hostPath mounts unless clearly required
  - broad RBAC wildcards unless justified
```

---

## Testing guidance

Possible validation commands:

```bash
kubectl apply --dry-run=client -f <file>
kubectl kustomize <dir>
helm template <chart>
kubeconform <file>
yamllint <file>
```

Only claim commands were run if actually run.

---

## Review checklist

Reviewer should check:

- YAML is valid
- resources have names and labels
- namespaces are correct
- secrets are referenced, not embedded
- RBAC is least privilege
- probes/resources are considered where appropriate
- deployment changes are reversible
- local and production assumptions are clear

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - committing secrets
  - overly broad RBAC
  - mixing local and production config without labels
  - changing many unrelated manifests
  - removing health checks without reason
  - introducing privileged pods casually
```

---

## Output note

If relevant, include:

```md
## Skills Applied
- kubernetes
```
