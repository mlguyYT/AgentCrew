# Small Bug Fix

## User Prompt

```text
Fix the login form so empty email shows a validation message.
```

## Expected AgentCrew Routing

```yaml
lane: Fast Lane
starting_role: Developer
recipe: bug-fix
quality_profile: standard
next_roles:
  - Tester
  - Reviewer if behavior or shared validation risk is meaningful
  - Human
```

## Expected Skills

```text
Load based on project detection and changed files.
For React/TypeScript: react + typescript-pro.
For backend validation: matching API/framework Skill.
```

## Useful Optional Commands

```bash
~/AgentCrew/bin/agentcrew classify --task "Fix the login form so empty email shows a validation message"
~/AgentCrew/bin/agentcrew start --task "Fix the login form so empty email shows a validation message"
~/AgentCrew/bin/agentcrew brief --task "Fix the login form so empty email shows a validation message"
```

## Expected Artifacts

```text
.agent-state/current-task.md when durable state helps
.agent-state/task-brief.md when acceptance criteria need to be explicit
.agent-state/test-report.md after validation
```

## Human Boundary

The agent may implement, test, and prepare the PR.
The human approves final PR and merge.
