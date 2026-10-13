# Idea-To-Product Playbook

## Purpose

Turn a normal-language product idea into a recommended direction and, after CEO approval, a validated implementation without asking the user to manage roles or workflow steps.

## Trigger

Use this playbook when the user describes a new product, startup, application, service, platform, substantial feature idea, or asks AgentCrew to shape an idea and build it.

## Discovery And Planning

AgentCrew selects the minimum useful team:

```text
Advisor
  -> Researcher Agent if external evidence is needed
  -> Idea Consultant
  -> Product Manager
  -> CEO direction and execution approval
```

Before the CEO gate, the team should determine:

- problem, target user, and expected value
- assumptions and evidence confidence
- feasibility and important constraints
- recommended direction and credible alternatives
- smallest useful MVP and explicit exclusions
- acceptance outcomes and delivery slices
- architecture or specialist work that will be required
- estimated execution cost, range, confidence, and stop conditions when available

Do not start implementation merely because the original message contains words such as `build`, `create`, or `develop`. First produce the decision-ready plan.

## CEO Gate

Present one compact recommendation using `agent-team/templates/executive-brief.md`.

Engine runs may encode the same fields in the Product Manager-to-Human compact handoff instead of creating a separate file.

Ask for a single explicit decision when practical:

```text
Approve this direction, MVP scope, and execution boundary?
```

Split the gate only when product direction, consequential architecture, material spend, or risk cannot safely be approved together.

## Delivery

After approval, AgentCrew creates the internal task graph and runs the minimum justified delivery team:

```text
Software Architect Agent if triggered
  -> Developer
  -> Tester
  -> Reviewer when risk is meaningful
  -> Specialist Reviewers if triggered
  -> CEO release or merge approval
```

AgentCrew owns task assignment, handoffs, safe parallelism, evidence collection, and bounded rework. The CEO does not need to invoke each role.

## Autonomous Decision Rule

The team resolves a decision without interruption when it is:

- reversible
- inside approved scope and budget
- compatible with project constraints and public contracts
- supported by evidence or established project conventions
- not reserved for the CEO by `agent-team/policies/ceo-operating-contract.md`

Record durable decisions in the current project's `.agent-state/decisions.md`.

## Stop Conditions

Stop and return to the CEO when:

- product direction or material scope is unresolved
- cost crosses the approved boundary
- a human-only risk or irreversible action appears
- evidence gates cannot pass after bounded rework
- release, deployment, PR approval, or merge is next
