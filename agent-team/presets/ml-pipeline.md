# ML Pipeline Preset

## Use When

Use for training pipelines, evaluation harnesses, inference services, or data-prep code in ML / data science projects.

## Default Skills

```text
python-pro
sql-pro when data sources are SQL
cnn when computer vision is part of the project
llm-pro when LLM tooling, prompts, or RAG are part of the project
```

## Architecture Focus

- separate data loading, transforms, training, evaluation, and inference
- pin model and dataset versions explicitly; never silently retrain
- isolate hyperparameters in config — never hard-code in training scripts
- gate any change to evaluation metrics, sampling, or random seeds

## Validation Defaults

- pytest for unit tests
- a small fixed eval set with deterministic seed for regression detection
- profiling check when touching training inner loops
- diff the evaluation metrics on the touched commit and report % change

## Review Gates

- LLM review when prompt, retrieval, tool-calling, or model-selection logic changes
- CNN review when vision model architecture, augmentation, or training loop changes
- dependency and supply-chain gate on requirements / Pipfile / poetry.lock changes
- behavior-preserving refactor check when changing training or eval code without intent to change metrics

## Required Specialists Suggestion

- LLM Agent on prompt / RAG / tool-use changes
- CNN Agent on vision model changes
- Security Reviewer on data-egress or PII-handling changes

## Config Defaults (suggested)

```yaml
quality_profile: strict
recipe_profiles:
  refactor: strict
required_specialists:
  - paths: ["**/prompts/**", "**/rag/**", "**/agents/**"]
    roles: ["LLM Agent"]
  - paths: ["**/models/**vision**", "**/cnn/**", "**/segmentation/**"]
    roles: ["CNN Agent"]
  - paths: ["**/data/loaders/**", "**/etl/**", "**/pii/**"]
    roles: ["Security Reviewer"]
```
