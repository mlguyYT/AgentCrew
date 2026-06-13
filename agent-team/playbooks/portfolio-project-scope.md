# Portfolio Project Scope

## Purpose

Use this playbook when the user wants to build, plan, or refine a portfolio, resume, interview, case-study, or target-role project.

The goal is not to maximize features. The goal is to produce clear evidence that the project proves the target role requirements.

---

## Default Route

```text
Product Manager
  -> Researcher Agent if job descriptions, role evidence, or market signals are needed
  -> Developer after human scope approval
  -> Tester
  -> Documentation Agent for resume/demo artifacts
  -> Human
```

Start with Product Manager unless the user only asks for source-backed job-market research.

---

## Inputs

Collect or infer only what is needed:

- target role or audience
- job description, posting, or role requirements if available
- project idea or rough domain
- time budget and desired depth
- must-have technologies
- portfolio constraints such as demoability, hosting, or interview story

Ask the human only when multiple directions would create materially different projects.

---

## Anti-Scope-Creep Rule

Every proposed feature must map to all three:

```text
job requirement -> project evidence -> interview talking point
```

Cut or defer anything that does not create hiring evidence.

Prefer a minimum convincing project over a large project:

- one target role first
- one strong product story
- one or two technically meaningful slices
- visible tests, architecture, and tradeoffs
- clear demo and README

Keep future enhancements separate from MVP scope.

---

## Output Artifacts

Use these artifacts when useful:

```text
.agent-state/role-fit-matrix.md
.agent-state/mvp-scope.md
.agent-state/resume-bullets.md
.agent-state/demo-script.md
```

Templates:

```text
agent-team/templates/role-fit-matrix.md
agent-team/templates/mvp-scope.md
agent-team/templates/resume-bullets.md
agent-team/templates/demo-script.md
```

---

## Human Gates

Human approval is required for:

- target role and project positioning
- MVP scope
- claims used in resume bullets, portfolio copy, or demo script
- tradeoffs that intentionally exclude common features

Do not let an agent silently expand scope to make the project look more impressive.

---

## Done

The portfolio plan is ready when:

- target role is explicit
- each MVP feature maps to a role requirement
- evidence artifacts are named
- over-scope risks are separated from MVP
- demo path is realistic
- resume claims are truthful and human-approved
