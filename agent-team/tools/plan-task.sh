#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: plan-task.sh --task TEXT [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --task TEXT         User request to plan"
  printf '%s\n' "  --project PATH      Target project path. Default: current directory"
  printf '%s\n' "  --force             Overwrite existing .agent-state/work-plan.md"
  printf '%s\n' "  --dry-run           Print the work plan without writing"
  printf '%s\n' "  -h, --help          Show help"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)" || exit 1
CLASSIFIER="$SCRIPT_DIR/classify-task.sh"

TASK=""
PROJECT="."
FORCE="false"
DRY_RUN="false"
POSITIONAL=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --task)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --task" >&2; exit 2; }
      TASK="$2"
      shift 2
      ;;
    --project)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --project" >&2; exit 2; }
      PROJECT="$2"
      shift 2
      ;;
    --force)
      FORCE="true"
      shift
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

if [ -z "$TASK" ] && [ "${#POSITIONAL[@]}" -gt 0 ]; then
  TASK="${POSITIONAL[*]}"
fi

if [ -z "$TASK" ]; then
  usage >&2
  exit 2
fi

if [ ! -d "$PROJECT" ]; then
  printf 'Project path does not exist: %s\n' "$PROJECT" >&2
  exit 1
fi

[ -x "$CLASSIFIER" ] || { printf 'Missing executable task classifier: %s\n' "$CLASSIFIER" >&2; exit 1; }

PROJECT_ABS="$(cd "$PROJECT" && pwd -P)" || exit 1
PROJECT_ROOT="$PROJECT_ABS"
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

STATE_DIR="$PROJECT_ROOT/.agent-state"
WORK_PLAN="$STATE_DIR/work-plan.md"
CLASSIFICATION="$($CLASSIFIER --project "$PROJECT_ROOT" --task "$TASK")" || exit 1

field_value() {
  printf '%s\n' "$CLASSIFICATION" |
    awk -v key="$1" '$0 ~ "^  " key ":" { sub("^  " key ": ", ""); print; exit }' |
    sed "s/^'//; s/'$//; s/''/'/g"
}

TASK_TEXT="$(field_value task)"
RISK="$(field_value risk)"
LANE="$(field_value lane)"
QUALITY_PROFILE="$(field_value quality_profile)"
RECIPE="$(field_value recipe)"
STARTING_ROLE="$(field_value starting_role)"
WORKFLOW="$(field_value workflow)"

[ -n "$TASK_TEXT" ] || TASK_TEXT="$TASK"
[ -n "$RISK" ] || RISK="unknown"
[ -n "$LANE" ] || LANE="unknown"
[ -n "$QUALITY_PROFILE" ] || QUALITY_PROFILE="standard"
[ -n "$RECIPE" ] || RECIPE="bug-fix"
[ -n "$STARTING_ROLE" ] || STARTING_ROLE="Developer"
[ -n "$WORKFLOW" ] || WORKFLOW="$STARTING_ROLE -> Human"

phase_lines() {
  case "$RECIPE" in
    bug-fix)
      cat <<EOF
### WP-001: Understand and isolate defect
- owner: Developer
- goal: identify the failing behavior and smallest affected area
- files_or_areas: inspect relevant code and tests
- acceptance: root cause or likely failure path is identified
- validation: focused reproduction or code evidence
- gates: escalate if scope or risk grows

### WP-002: Implement focused fix
- owner: Developer
- goal: change only what is needed to address the defect
- files_or_areas: affected implementation and tests
- acceptance: reported defect no longer occurs
- validation: focused regression test or documented limitation
- gates: Tester validation
EOF
      ;;
    feature)
      cat <<EOF
### WP-001: Confirm scope and acceptance
- owner: Product Manager
- goal: make the feature small enough for a focused PR
- files_or_areas: product flow, API, UI, data model as applicable
- acceptance: scope and out-of-scope behavior are explicit
- validation: task brief or acceptance criteria reviewed
- gates: human decision if product behavior is materially ambiguous

### WP-002: Implement first vertical slice
- owner: Developer
- goal: deliver the smallest usable feature path
- files_or_areas: implementation and tests for the first slice
- acceptance: primary flow works as scoped
- validation: focused tests and manual checks when relevant
- gates: Tester, Reviewer, Specialist when triggered

### WP-003: Validate and document
- owner: Tester / Documentation Agent
- goal: verify acceptance criteria and update docs if public behavior changed
- files_or_areas: tests, README, guides, changelog as needed
- acceptance: validation evidence and docs are ready for human review
- validation: test report plus docs review when needed
- gates: Human approval
EOF
      ;;
    refactor)
      cat <<EOF
### WP-001: Lock preserved behavior
- owner: Developer
- goal: identify behavior that must remain unchanged
- files_or_areas: affected modules, tests, public interfaces
- acceptance: preserved behavior and boundaries are explicit
- validation: existing tests or characterization checks identified
- gates: Reviewer if shared module or large diff

### WP-002: Extract one boundary
- owner: Developer
- goal: make one structural improvement without behavior change
- files_or_areas: one module or boundary at a time
- acceptance: public behavior, schemas, keys, and events remain stable
- validation: focused tests pass
- gates: behavior-preserving refactor check
EOF
      ;;
    docs-update)
      cat <<EOF
### WP-001: Verify source of truth
- owner: Documentation Agent
- goal: identify the real behavior, paths, and commands to document
- files_or_areas: docs, examples, README, changelog
- acceptance: documentation claims are backed by repository evidence
- validation: commands or paths are checked where practical
- gates: Reviewer if behavior claims changed
EOF
      ;;
    review)
      cat <<EOF
### WP-001: Review diff or artifact
- owner: Reviewer
- goal: identify blocking issues, risks, test gaps, and product decisions
- files_or_areas: changed files or requested artifact
- acceptance: findings are separated by severity and decision type
- validation: review report uses AgentCrew output discipline
- gates: Specialist Reviewer when triggered
EOF
      ;;
    validation)
      cat <<EOF
### WP-001: Map checks to acceptance criteria
- owner: Tester
- goal: decide focused and broad validation needed
- files_or_areas: tests, affected flows, reports
- acceptance: validation plan maps to criteria and risk
- validation: commands run or limitations documented
- gates: Reviewer when risk is meaningful
EOF
      ;;
    research)
      cat <<EOF
### WP-001: Define decision criteria
- owner: Researcher Agent
- goal: make the research question decision-ready
- files_or_areas: sources, docs, standards, options
- acceptance: facts, assumptions, confidence, and recommendation are separated
- validation: source quality check
- gates: Product Manager or Human if decision is needed
EOF
      ;;
    release)
      cat <<EOF
### WP-001: Check release readiness
- owner: Tester / Reviewer
- goal: verify branch, validation baseline, changelog, and risks
- files_or_areas: release notes, changelog, version, CI, package files
- acceptance: release readiness checklist is satisfied or gaps are documented
- validation: full validation appropriate to project
- gates: Human release, merge, or deploy approval
EOF
      ;;
    incident)
      cat <<EOF
### WP-001: Stabilize and choose mitigation
- owner: Advisor / Product Manager
- goal: choose the smallest safe mitigation or rollback path
- files_or_areas: affected production flow, config, deploy state
- acceptance: human-only risk decisions are explicit
- validation: mitigation can be verified quickly
- gates: Human decision for rollback, security, data, or customer-impact risk

### WP-002: Implement or prepare mitigation
- owner: Developer
- goal: make the smallest reversible change
- files_or_areas: affected hotfix area only
- acceptance: urgent regression is mitigated
- validation: focused production-like check or rollback evidence
- gates: Tester, Reviewer, Specialist when triggered
EOF
      ;;
    skill-change)
      cat <<EOF
### WP-001: Validate skill change
- owner: Skill Validator
- goal: verify triggers, safety, registry path, and examples
- files_or_areas: skill file, registry, authoring guide
- acceptance: Skill validation report is ready
- validation: checklist and registry path check
- gates: Human approval
EOF
      ;;
    *)
      cat <<EOF
### WP-001: Plan focused change
- owner: $STARTING_ROLE
- goal: make the next action small and testable
- files_or_areas: to be identified by selected owner
- acceptance: requested outcome is addressed
- validation: focused validation or documented limitation
- gates: Human approval
EOF
      ;;
  esac
}

artifact() {
  printf '# Work Plan\n\n'
  printf '## Title\n%s\n\n' "$TASK_TEXT"
  printf '## Request\n%s\n\n' "$TASK_TEXT"
  printf '## Recipe\n%s\n\n' "$RECIPE"
  printf '## Lane\n%s\n\n' "$LANE"
  printf '## Risk\n%s\n\n' "$RISK"
  printf '## Quality Profile\n%s\n\n' "$QUALITY_PROFILE"
  printf '## Workflow\n%s\n\n' "$WORKFLOW"
  printf '## Planning Assumptions\n- Plan generated from request classification; refine after inspecting project files.\n\n'
  printf '## Phases\n\n'
  phase_lines
  printf '\n## Human Decisions\n- Final approval remains human-only. Add specific decisions when risk, product direction, public behavior, migration, or security tradeoffs appear.\n\n'
  printf '## Risks\n- Risk level: %s. Escalate if implementation touches a higher-risk area than the request suggests.\n\n' "$RISK"
  printf '## Next Action\n%s should inspect relevant files and start with the first phase.\n\n' "$STARTING_ROLE"
  printf '## Handoff\n\n'
  printf '### Context\n- Work plan generated from AgentCrew routing and recipe selection.\n\n'
  printf '### Decision\nPlan follows recipe `%s` with lane `%s`.\n\n' "$RECIPE" "$LANE"
  printf '### Evidence\n- Quality profile: %s\n- Workflow: %s\n\n' "$QUALITY_PROFILE" "$WORKFLOW"
  printf '### Next Action\n%s should execute WP-001 or refine the plan if project inspection changes risk.\n\n' "$STARTING_ROLE"
  printf '### Open Questions\nOnly blockers.\n'
}

if [ "$DRY_RUN" = "true" ]; then
  artifact
  exit 0
fi

if [ -f "$WORK_PLAN" ] && [ "$FORCE" != "true" ]; then
  printf '%s\n' "Refusing to overwrite existing work plan: $WORK_PLAN" >&2
  printf '%s\n' "Use --force to replace it, or save the previous plan first." >&2
  exit 1
fi

mkdir -p "$STATE_DIR" || exit 1
artifact > "$WORK_PLAN" || exit 1

SENSITIVE_PATTERN='[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}|/home/[^[:space:]]+|/Users/[^[:space:]]+|[A-Za-z]:\\Users\\|\.ssh/|id_rsa|id_ed25519|deploy[-_ ]?key'
if grep -Eiq "$SENSITIVE_PATTERN" "$WORK_PLAN"; then
  rm -f "$WORK_PLAN"
  printf '%s\n' 'Refusing to save work plan: generated artifact contains personal identifiers, private key paths, deploy-key paths, or local machine paths.' >&2
  exit 1
fi

printf '%s\n' "AGENTCREW WORK PLAN CREATED"
printf '%s\n' "File: $WORK_PLAN"
printf '%s\n' "Recipe: $RECIPE"
printf '%s\n' "Lane: $LANE"
printf '%s\n' "Owner: $STARTING_ROLE"
