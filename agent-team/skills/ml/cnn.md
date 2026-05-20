# Skill: CNN

## Purpose

Use this skill for computer vision and convolutional neural network work involving image datasets, preprocessing, model training, evaluation, inference, and deployment.

---

## Applies when

Use this skill when work involves:

- computer vision
- convolutional neural networks
- image classification
- object detection
- segmentation
- image preprocessing or augmentation
- dataset labels and splits
- training or evaluating vision models
- inference optimization or deployment constraints

---

## Detection triggers

```yaml
triggers:
  text:
    - CNN
    - convolutional neural network
    - computer vision
    - image classification
    - object detection
    - segmentation
    - image dataset
    - augmentation
    - preprocessing
    - inference optimization
    - PyTorch vision
    - TensorFlow vision
  files:
    - "datasets/**"
    - "models/**"
    - "notebooks/**"
    - "**/*vision*"
    - "**/*cnn*"
```

---

## Instructions

- Start with dataset and label assumptions before model architecture.
- Check train/validation/test split integrity and leakage risk.
- Match metrics to the task and failure cost.
- Track overfitting, reproducibility, and baseline comparisons.
- Keep preprocessing consistent between training and inference.
- Document deployment constraints such as latency, memory, model size, and target hardware.

---

## Testing guidance

- Validate dataset loading, preprocessing, and inference paths.
- Distinguish train, validation, test, and production metrics.
- Include small smoke tests for pipeline correctness when full training is expensive.
- Record random seeds, versions, and hardware constraints when relevant.

---

## Review checklist

- dataset split is clear
- leakage risk checked
- label quality understood
- metrics fit task
- augmentation justified
- overfitting monitored
- inference constraints documented
- sensitive image data handled safely

---

## Anti-patterns

Avoid:

- reporting training accuracy as deployment readiness
- ignoring dataset leakage or label noise
- optimizing architecture before understanding data quality
- deploying low-confidence models without human approval
- mixing preprocessing between training and inference
