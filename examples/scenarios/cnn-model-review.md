# CNN Model Review

## User Prompt

```text
Review this image classification training pipeline for data leakage, label quality, metrics, overfitting, augmentation, and inference constraints.
```

## Expected AgentCrew Routing

```yaml
starting_role: CNN Agent
required_skills:
  - cnn
next_roles:
  - Researcher Agent if source-backed benchmark or model comparison is needed
  - Developer if pipeline changes are needed
  - Tester if validation or evaluation checks are needed
  - Human
```

## Expected Artifacts

```text
.agent-state/cnn-report.md when durable review context helps
.agent-state/research-report.md if source-backed external comparison is needed
.agent-state/test-report.md when validation runs
```

## Review Focus

- dataset splits and leakage
- label quality
- metrics and class imbalance
- augmentation and preprocessing
- overfitting and generalization
- inference latency, memory, and deployment constraints

## Human Boundary

Agents may recommend model or pipeline changes.
The human approves product-risk acceptance, deployment decision, and release.
