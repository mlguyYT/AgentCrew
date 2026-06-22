# Project Constraints

## Standing Constraints

- Keep project-specific constraints here.

## Workflow Boundary

- AgentCrew remains the project routing and discipline layer unless the human explicitly changes it.

## Commit Policy

- commits_allowed: true
- pushes_allowed: false
- approval_required: explicit per action

## Public Private Boundary

- public_repo:
- private_local:
- separate_workspace:
- never_public:

## Sensitive Wording

- avoid:
- allowed:

## Cloud Resources

- cost_bearing_actions_need_confirmation: true
- teardown_required: true
- resource_state_file: `.agent-state/cloud-resources.md`

## Generated Or Temporary Files

- specs:
- chunks:
- logs:
- outputs:

## Next Safe Action

State the next action that respects these constraints.

