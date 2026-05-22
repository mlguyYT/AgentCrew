# Scenario Examples

These scenarios show how AgentCrew should route normal user requests without requiring the user to name a role, lane, or Skill.

Use them as copyable examples for demos, onboarding, docs, or manual testing.

```text
Open any project and ask for the outcome.
AgentCrew should classify the request, choose the lane, choose the starting role, load relevant Skills, and stop at human approval.
```

## Scenarios

- [Small bug fix](small-bug-fix.md)
- [Customer support triage](customer-support-triage.md)
- [Risky auth change](risky-auth-change.md)
- [Release preparation](release-preparation.md)
- [LLM feature review](llm-feature-review.md)
- [CNN model review](cnn-model-review.md)

## Rules

- Users may ask naturally.
- Role-specific prompts are optional.
- Agents should keep `.agent-state/` project-local.
- Human approval remains final.
