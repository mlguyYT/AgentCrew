# CNN Review Checklist

## Purpose

Use this checklist for computer vision and convolutional neural network work.

---

## Dataset

- [ ] train/validation/test split is clear
- [ ] leakage risk is checked
- [ ] label quality is understood
- [ ] class imbalance is considered
- [ ] sensitive image data is handled safely

---

## Model And Training

- [ ] metrics match the task and failure cost
- [ ] augmentation is justified
- [ ] overfitting is monitored
- [ ] training is reproducible enough for the project
- [ ] baseline comparison exists when useful

---

## Inference And Deployment

- [ ] preprocessing matches training
- [ ] latency and resource constraints are documented
- [ ] model size and target hardware are considered
- [ ] monitoring or drift risk is documented when production deployment is involved

---

## Human Decision

Human approval is required for sensitive image data, fairness/safety risk, low-confidence deployment, or accepting limited dataset coverage.
