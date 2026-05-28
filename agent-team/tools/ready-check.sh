#!/usr/bin/env bash
set -u

usage() {
  printf '%s
' "Usage: ready-check.sh [options]"
  printf '%s
' ""
  printf '%s
' "Options:"
  printf '%s
' "  --project PATH      Target project path. Default: current directory"
  printf '%s
' "  --force             Overwrite existing .agent-state/readiness-report.md"
  printf '%s
' "  --dry-run           Print the readiness report without writing"
  printf '%s
' "  -h, --help          Show help"
}

PROJECT="."
FORCE="false"
DRY_RUN="false"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      [ "$#" -ge 2 ] || { printf '%s
' "Missing value for --project" >&2; exit 2; }
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
    *)
      printf 'Unknown option: %s
' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ ! -d "$PROJECT" ]; then
  printf 'Project path does not exist: %s
' "$PROJECT" >&2
  exit 1
fi

PROJECT_ABS="$(cd "$PROJECT" && pwd -P)" || exit 1
PROJECT_ROOT="$PROJECT_ABS"
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

# Refuse to write outside $HOME unless the project is a git worktree
# (security review INFO-3).
case "$PROJECT_ROOT" in
  "$HOME"|"$HOME"/*) ;;
  *)
    if ! git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      printf 'Refusing to write under %s: outside $HOME and not a git worktree.\n' "$PROJECT_ROOT" >&2
      exit 1
    fi
    ;;
esac

PROJECT_NAME="$(basename "$PROJECT_ROOT")"
STATE_DIR="$PROJECT_ROOT/.agent-state"
CURRENT_TASK="$STATE_DIR/current-task.md"
TASK_BRIEF="$STATE_DIR/task-brief.md"
WORK_PLAN="$STATE_DIR/work-plan.md"
HUMAN_DECISIONS="$STATE_DIR/human-decisions.md"
READINESS_REPORT="$STATE_DIR/readiness-report.md"

section_value() {
  local file="$1"
  local heading="$2"
  [ -f "$file" ] || return 1
  awk -v heading="$heading" '
    $0 == "## " heading { in_section = 1; next }
    in_section && /^## / { exit }
    in_section && NF { print; exit }
  ' "$file"
}

has_pending_decision() {
  local file="$1"
  [ -f "$file" ] || return 1
  awk '
    /^## Pending Decisions/ { in_pending = 1; next }
    in_pending && /^## / { exit }
    in_pending && /^### / { found = 1 }
    END { exit found ? 0 : 1 }
  ' "$file"
}

BLOCKERS=()
WARNINGS=()
RECOMMENDATION="proceed_to_developer"
STATUS="ready"

add_blocker() {
  BLOCKERS+=("$1")
  STATUS="not_ready"
}

add_warning() {
  WARNINGS+=("$1")
}

if [ -f "$CURRENT_TASK" ]; then
  CURRENT_TASK_STATUS="present"
else
  CURRENT_TASK_STATUS="missing"
  add_blocker "current task is missing; run agentcrew start or provide a clearly routed request"
  RECOMMENDATION="create_current_task"
fi

if [ -f "$TASK_BRIEF" ]; then
  TASK_BRIEF_STATUS="present"
else
  TASK_BRIEF_STATUS="missing"
fi

if [ -f "$WORK_PLAN" ]; then
  WORK_PLAN_STATUS="present"
else
  WORK_PLAN_STATUS="missing"
fi

LANE="$(section_value "$CURRENT_TASK" "Lane")"
RISK="$(section_value "$CURRENT_TASK" "Risk")"
RECIPE="$(section_value "$CURRENT_TASK" "Recipe")"
OWNER="$(section_value "$CURRENT_TASK" "Owner")"
NEXT_ACTION="$(section_value "$CURRENT_TASK" "Next Action")"
OPEN_QUESTIONS="$(section_value "$CURRENT_TASK" "Open Questions")"

[ -n "$LANE" ] || LANE="unknown"
[ -n "$RISK" ] || RISK="unknown"
[ -n "$RECIPE" ] || RECIPE="unknown"
[ -n "$OWNER" ] || OWNER="unknown"

if [ "$CURRENT_TASK_STATUS" = "present" ] && { [ -z "$OWNER" ] || [ "$OWNER" = "unknown" ]; }; then
  add_blocker "current task owner is not set"
  RECOMMENDATION="clarify_scope"
fi

if [ "$CURRENT_TASK_STATUS" = "present" ] && { [ -z "$NEXT_ACTION" ] || [ "$NEXT_ACTION" = "not set" ]; }; then
  add_blocker "next action is not set"
  RECOMMENDATION="clarify_scope"
fi

case "$RISK:$LANE:$RECIPE" in
  *high*|*critical*|*Full\ Lane*|*incident*|*release*)
    if [ "$WORK_PLAN_STATUS" = "missing" ]; then
      add_blocker "work plan is missing for high-risk, Full Lane, release, incident, or broad work"
      RECOMMENDATION="create_work_plan"
    fi
    ;;
  *medium*|*feature*|*refactor*)
    if [ "$TASK_BRIEF_STATUS" = "missing" ]; then
      add_warning "task brief is recommended for medium-risk, feature, or refactor work"
      [ "$RECOMMENDATION" = "proceed_to_developer" ] && RECOMMENDATION="create_task_brief"
    fi
    ;;
esac

if [ "$TASK_BRIEF_STATUS" = "missing" ] && [ "$CURRENT_TASK_STATUS" = "present" ] && [ "$RISK" != "low" ]; then
  add_blocker "task brief is missing for non-low-risk work"
  RECOMMENDATION="create_task_brief"
fi

if has_pending_decision "$HUMAN_DECISIONS"; then
  HUMAN_DECISION_STATUS="pending"
  add_blocker "pending human decision exists"
  RECOMMENDATION="resolve_human_decision"
else
  if [ -f "$HUMAN_DECISIONS" ]; then
    HUMAN_DECISION_STATUS="clear"
  else
    HUMAN_DECISION_STATUS="not set"
  fi
fi

if printf '%s
' "$OPEN_QUESTIONS" | grep -Eiq 'block|blocked|unknown|todo|\?'; then
  add_blocker "open questions may block implementation"
  [ "$RECOMMENDATION" = "proceed_to_developer" ] && RECOMMENDATION="clarify_scope"
fi

if [ "$STATUS" = "ready" ] && [ "$RECOMMENDATION" != "proceed_to_developer" ]; then
  add_warning "recommended preparation exists but does not block tiny low-risk work"
fi

print_list() {
  local empty_text="$1"
  shift
  if [ "$#" -eq 0 ]; then
    printf -- '- %s
' "$empty_text"
    return
  fi
  local item
  for item in "$@"; do
    printf -- '- %s
' "$item"
  done
}

artifact() {
  printf '# Readiness Report

'
  printf '## Status
%s

' "$STATUS"
  printf '## Project
%s

' "$PROJECT_NAME"
  printf '## Current Task
%s

' "$CURRENT_TASK_STATUS"
  printf '## Task Brief
%s

' "$TASK_BRIEF_STATUS"
  printf '## Work Plan
%s

' "$WORK_PLAN_STATUS"
  printf '## Human Decisions
%s

' "$HUMAN_DECISION_STATUS"
  printf '## Route Snapshot
- lane: %s
- risk: %s
- recipe: %s
- owner: %s

' "$LANE" "$RISK" "$RECIPE" "$OWNER"
  printf '## Blocking Issues
'
  print_list "None" "${BLOCKERS[@]}"
  printf '
## Warnings
'
  print_list "None" "${WARNINGS[@]}"
  printf '
## Recommendation
%s

' "$RECOMMENDATION"
  printf '## Next Action
'
  case "$RECOMMENDATION" in
    create_current_task) printf '%s
' 'Run agentcrew start or route the request before implementation.' ;;
    create_task_brief) printf '%s
' 'Run agentcrew brief or have Product Manager clarify acceptance criteria.' ;;
    create_work_plan) printf '%s
' 'Run agentcrew plan or have Product Manager slice the work before implementation.' ;;
    resolve_human_decision) printf '%s
' 'Ask the human to resolve pending human-only decisions before implementation.' ;;
    clarify_scope) printf '%s
' 'Clarify owner, next action, or blocking open questions before implementation.' ;;
    *) printf '%s
' 'Proceed to Developer using the current task, brief, and work plan context.' ;;
  esac
  printf '
## Handoff

'
  printf '### Context
- Readiness check evaluated AgentCrew project-state artifacts.

'
  printf '### Decision
Implementation readiness: %s.

' "$STATUS"
  printf '### Evidence
- current_task: %s
- task_brief: %s
- work_plan: %s
- human_decisions: %s

' "$CURRENT_TASK_STATUS" "$TASK_BRIEF_STATUS" "$WORK_PLAN_STATUS" "$HUMAN_DECISION_STATUS"
  printf '### Next Action
Follow the recommendation above.

'
  printf '### Open Questions
Only blockers.
'
}

if [ "$DRY_RUN" = "true" ]; then
  artifact
  exit 0
fi

if [ -f "$READINESS_REPORT" ] && [ "$FORCE" != "true" ]; then
  printf '%s
' "Refusing to overwrite existing readiness report: $READINESS_REPORT" >&2
  printf '%s
' "Use --force to replace it." >&2
  exit 1
fi

mkdir -p "$STATE_DIR" || exit 1
artifact > "$READINESS_REPORT" || exit 1

SENSITIVE_PATTERN='[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}|/home/[^[:space:]]+|/Users/[^[:space:]]+|[A-Za-z]:\\Users\\|\.ssh/|id_rsa|id_ed25519|deploy[-_ ]?key'
if grep -Eiq "$SENSITIVE_PATTERN" "$READINESS_REPORT"; then
  rm -f "$READINESS_REPORT"
  printf '%s
' 'Refusing to save readiness report: generated artifact contains personal identifiers, private key paths, deploy-key paths, or local machine paths.' >&2
  exit 1
fi

printf '%s
' "AGENTCREW READINESS CHECK COMPLETE"
printf '%s
' "File: $READINESS_REPORT"
printf '%s
' "Status: $STATUS"
printf '%s
' "Recommendation: $RECOMMENDATION"
