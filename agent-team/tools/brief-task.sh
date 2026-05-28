#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: brief-task.sh --task TEXT [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --task TEXT         User request to brief"
  printf '%s\n' "  --project PATH      Target project path. Default: current directory"
  printf '%s\n' "  --force             Overwrite existing .agent-state/task-brief.md"
  printf '%s\n' "  --dry-run           Print the task brief without writing"
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

STATE_DIR="$PROJECT_ROOT/.agent-state"
TASK_BRIEF="$STATE_DIR/task-brief.md"
CLASSIFICATION="$($CLASSIFIER --project "$PROJECT_ROOT" --task "$TASK")" || exit 1

field_value() {
  printf '%s\n' "$CLASSIFICATION" |
    awk -v key="$1" '$0 ~ "^  " key ":" { sub("^  " key ": ", ""); print; exit }' |
    sed "s/^'//; s/'$//; s/''/'/g"
}

TASK_TEXT="$(field_value task)"
INTENT="$(field_value intent)"
RISK="$(field_value risk)"
LANE="$(field_value lane)"
QUALITY_PROFILE="$(field_value quality_profile)"
RECIPE="$(field_value recipe)"
STARTING_ROLE="$(field_value starting_role)"
WORKFLOW="$(field_value workflow)"

[ -n "$TASK_TEXT" ] || TASK_TEXT="$TASK"
[ -n "$INTENT" ] || INTENT="not classified"
[ -n "$RISK" ] || RISK="unknown"
[ -n "$LANE" ] || LANE="unknown"
[ -n "$QUALITY_PROFILE" ] || QUALITY_PROFILE="standard"
[ -n "$RECIPE" ] || RECIPE="bug-fix"
[ -n "$STARTING_ROLE" ] || STARTING_ROLE="Developer"
[ -n "$WORKFLOW" ] || WORKFLOW="$STARTING_ROLE -> Human"

criteria_for_recipe() {
  case "$RECIPE" in
    bug-fix)
      printf '%s\n' '- [ ] reported defect no longer occurs'
      printf '%s\n' '- [ ] expected behavior is preserved for nearby flows'
      printf '%s\n' '- [ ] regression evidence is added or test limitation is documented'
      ;;
    feature)
      printf '%s\n' '- [ ] primary user flow works as requested'
      printf '%s\n' '- [ ] success, failure, and empty states are handled where relevant'
      printf '%s\n' '- [ ] user-visible behavior is documented or intentionally unchanged elsewhere'
      ;;
    refactor)
      printf '%s\n' '- [ ] external behavior remains unchanged'
      printf '%s\n' '- [ ] public APIs, data keys, schemas, and event names are preserved unless explicitly scoped'
      printf '%s\n' '- [ ] focused tests or validation cover preserved behavior'
      ;;
    docs-update)
      printf '%s\n' '- [ ] documented paths and commands match the repository'
      printf '%s\n' '- [ ] usage guidance is concise and current'
      printf '%s\n' '- [ ] behavior claims are verified or marked as assumptions'
      ;;
    review)
      printf '%s\n' '- [ ] blocking issues are separated from non-blocking risks'
      printf '%s\n' '- [ ] test gaps and product decisions are called out'
      printf '%s\n' '- [ ] rework is routed to the correct role when needed'
      ;;
    validation)
      printf '%s\n' '- [ ] relevant checks are run or limitations are documented'
      printf '%s\n' '- [ ] failures include concise reproduction or evidence'
      printf '%s\n' '- [ ] recommendation is clear: pass, rework, or human decision'
      ;;
    research)
      printf '%s\n' '- [ ] decision-relevant sources are cited or listed'
      printf '%s\n' '- [ ] facts, assumptions, and recommendations are separated'
      printf '%s\n' '- [ ] confidence and open questions are stated'
      ;;
    release)
      printf '%s\n' '- [ ] release notes or changelog reflect shipped behavior'
      printf '%s\n' '- [ ] validation baseline is documented'
      printf '%s\n' '- [ ] final release, merge, or deployment decision remains human-only'
      ;;
    incident)
      printf '%s\n' '- [ ] mitigation target is clear and narrow'
      printf '%s\n' '- [ ] validation proves the urgent regression is addressed or rollback is ready'
      printf '%s\n' '- [ ] follow-up root cause or hardening work is documented separately'
      ;;
    skill-change)
      printf '%s\n' '- [ ] skill trigger is specific and registry path is correct'
      printf '%s\n' '- [ ] skill does not override safety or human approval rules'
      printf '%s\n' '- [ ] Skill Validator output is documented'
      ;;
    *)
      printf '%s\n' '- [ ] requested outcome is addressed'
      printf '%s\n' '- [ ] validation evidence is documented'
      ;;
  esac
}

artifact() {
  printf '# Task Brief\n\n'
  printf '## Title\n%s\n\n' "$TASK_TEXT"
  printf '## Request\n%s\n\n' "$TASK_TEXT"
  printf '## Intent\n%s\n\n' "$INTENT"
  printf '## Recipe\n%s\n\n' "$RECIPE"
  printf '## Lane\n%s\n\n' "$LANE"
  printf '## Risk\n%s\n\n' "$RISK"
  printf '## Quality Profile\n%s\n\n' "$QUALITY_PROFILE"
  printf '## Owner\n%s\n\n' "$STARTING_ROLE"
  printf '## Workflow\n%s\n\n' "$WORKFLOW"
  printf '## Outcome\n%s\n\n' "$TASK_TEXT"
  printf '## User Or Operator Impact\n- To be refined by the selected role if the impact is not obvious from the request.\n\n'
  printf '## Acceptance Criteria\n'
  criteria_for_recipe
  printf '\n## Scope\n- Work directly needed for this request.\n\n'
  printf '## Out Of Scope\n- Unrelated refactors or behavior changes unless explicitly approved.\n\n'
  printf '## Test Plan\n- Run focused validation for the changed behavior, or document why validation is unavailable.\n\n'
  printf '## Review And Gates\n- Lane: %s\n- Quality profile: %s\n- Recipe: %s\n- Human approval remains final.\n\n' "$LANE" "$QUALITY_PROFILE" "$RECIPE"
  printf '## Open Questions\n- None recorded yet.\n\n'
  printf '## Handoff\n\n'
  printf '### Context\n- Task brief generated from request and AgentCrew routing.\n\n'
  printf '### Decision\n%s is the starting owner for this task.\n\n' "$STARTING_ROLE"
  printf '### Evidence\n- Recipe: %s\n- Workflow: %s\n\n' "$RECIPE" "$WORKFLOW"
  printf '### Next Action\n%s should refine the brief if needed, then continue through the routed workflow.\n\n' "$STARTING_ROLE"
  printf '### Open Questions\nOnly blockers.\n'
}

if [ "$DRY_RUN" = "true" ]; then
  artifact
  exit 0
fi

if [ -f "$TASK_BRIEF" ] && [ "$FORCE" != "true" ]; then
  printf '%s\n' "Refusing to overwrite existing task brief: $TASK_BRIEF" >&2
  printf '%s\n' "Use --force to replace it, or save the previous brief first." >&2
  exit 1
fi

mkdir -p "$STATE_DIR" || exit 1
artifact > "$TASK_BRIEF" || exit 1

SENSITIVE_PATTERN='[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}|/home/[^[:space:]]+|/Users/[^[:space:]]+|[A-Za-z]:\\Users\\|\.ssh/|id_rsa|id_ed25519|deploy[-_ ]?key'
if grep -Eiq "$SENSITIVE_PATTERN" "$TASK_BRIEF"; then
  rm -f "$TASK_BRIEF"
  printf '%s\n' 'Refusing to save task brief: generated artifact contains personal identifiers, private key paths, deploy-key paths, or local machine paths.' >&2
  exit 1
fi

printf '%s\n' "AGENTCREW TASK BRIEF CREATED"
printf '%s\n' "File: $TASK_BRIEF"
printf '%s\n' "Recipe: $RECIPE"
printf '%s\n' "Lane: $LANE"
printf '%s\n' "Owner: $STARTING_ROLE"
