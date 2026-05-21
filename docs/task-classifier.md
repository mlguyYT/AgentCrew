# Task Classifier

## Purpose

`agentcrew classify` gives a quick, read-only routing recommendation for a user request.

It helps agents and humans see the likely lane, starting role, reviewers, specialist triggers, Skill hints, gates, and files to load before work starts.

The classifier is heuristic. It does not replace repository inspection, AgentCrew playbooks, or human approval.

---

## Run

From a project directory:

```bash
~/AgentCrew/bin/agentcrew classify "Fix the login form so empty email shows a validation message"
```

With an explicit project path:

```bash
~/AgentCrew/bin/agentcrew classify --project /path/to/project --task "Change API token validation"
```

The standalone tool is also available inside AgentCrew:

```bash
~/AgentCrew/agent-team/tools/classify-task.sh --project /path/to/project --task "Add OAuth login"
```

---

## Output

The command prints compact YAML:

```yaml
task_classification:
  task: 'Add OAuth login'
  intent: 'implementation_or_bug_fix'
  risk: 'high'
  lane: 'Full Lane'
  quality_profile: 'strict'
  starting_role: 'Advisor'
  workflow: 'Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human'
  specialists:
    - 'Security Reviewer'
  gates:
    - 'tester validation'
    - 'full validation'
    - 'specialist review when triggered'
```

Use this output as a routing aid. Agents still need to inspect the task-specific files and project instructions.

To turn the classification into a project-local current task, use `agentcrew start`.

---

## What It Classifies

The classifier estimates:

- user intent
- risk level
- Fast Lane vs Full Lane
- starting role
- selected quality profile
- likely next roles
- required reviewers
- specialist triggers
- Skill hints
- quality gates
- human-only decision points
- AgentCrew files to load next

---

## Good Uses

Use it to quickly answer:

```text
What lane should this task use?
Which role should start?
Does this need Security Reviewer or Product Manager?
Which AgentCrew files should an agent load first?
```

It is especially useful for teams that want to understand why AgentCrew routes a request a certain way.

---

## Limits

The classifier uses request text and lightweight project context. It may miss risks that only appear in code, diffs, dependencies, or runtime behavior.

Agents must still follow:

```text
agent-team/context/route-index.md
agent-team/playbooks/request-routing.md
agent-team/playbooks/task-classification.md
agent-team/playbooks/quality-profile-selection.md
agent-team/playbooks/lane-escalation.md
```

When uncertain, choose the safer lane or ask the human.
