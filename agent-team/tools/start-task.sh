#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: start-task.sh --task TEXT [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --task TEXT         User request to start"
  printf '%s\n' "  --project PATH      Target project path. Default: current directory"
  printf '%s\n' "  --force             Overwrite existing .agent-state/current-task.md"
  printf '%s\n' "  --dry-run           Print the current-task artifact without writing"
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
CURRENT_TASK="$STATE_DIR/current-task.md"

CLASSIFICATION="$($CLASSIFIER --project "$PROJECT_ROOT" --task "$TASK")" || exit 1

field_value() {
  printf '%s\n' "$CLASSIFICATION" | awk -v key="$1" '
    $0 ~ "^  " key ":" {
      sub("^  " key ": ", "")
      gsub(/^'\''|'\''$/, "")
      print
      exit
    }
  '
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

artifact() {
  printf '# Current Task\n\n'
  printf '## Title\n%s\n\n' "$TASK_TEXT"
  printf '## Request\n%s\n\n' "$TASK_TEXT"
  printf '## Intent\n%s\n\n' "$INTENT"
  printf '## Lane\n%s\n\n' "$LANE"
  printf '## Risk\n%s\n\n' "$RISK"
  printf '## Quality Profile\n%s\n\n' "$QUALITY_PROFILE"
  printf '## Recipe\n%s\n\n' "$RECIPE"
  printf '## Owner\n%s\n\n' "$STARTING_ROLE"
  printf '## Workflow\n%s\n\n' "$WORKFLOW"
  printf '## Acceptance Criteria\n- To be refined by the selected role before implementation when the request is ambiguous.\n\n'
  printf '## Status\nStarted by AgentCrew task intake.\n\n'
  printf '## Next Action\n%s should inspect the relevant project files, refine acceptance criteria if needed, then continue through the routed workflow.\n\n' "$STARTING_ROLE"
  printf '## Open Questions\n- None recorded yet.\n\n'
  printf '## Safety\nThis artifact intentionally avoids secrets, raw customer data, personal identifiers, local machine paths, private key paths, and long logs.\n'
}

if [ "$DRY_RUN" = "true" ]; then
  artifact
  exit 0
fi

if [ -f "$CURRENT_TASK" ] && [ "$FORCE" != "true" ]; then
  printf '%s\n' "Refusing to overwrite existing current task: $CURRENT_TASK" >&2
  printf '%s\n' "Use --force to replace it, or move the existing task into a session checkpoint first." >&2
  exit 1
fi

mkdir -p "$STATE_DIR" || exit 1
artifact > "$CURRENT_TASK" || exit 1

SENSITIVE_PATTERN='[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}|/home/[^[:space:]]+|/Users/[^[:space:]]+|[A-Za-z]:\\Users\\|\.ssh/|id_rsa|id_ed25519|deploy[-_ ]?key'
if grep -Eiq "$SENSITIVE_PATTERN" "$CURRENT_TASK"; then
  rm -f "$CURRENT_TASK"
  printf '%s\n' 'Refusing to save current task: generated artifact contains personal identifiers, private key paths, deploy-key paths, or local machine paths.' >&2
  exit 1
fi

printf '%s\n' "AGENTCREW TASK STARTED"
printf '%s\n' "File: $CURRENT_TASK"
printf '%s\n' "Lane: $LANE"
printf '%s\n' "Quality profile: $QUALITY_PROFILE"
printf '%s\n' "Recipe: $RECIPE"
printf '%s\n' "Owner: $STARTING_ROLE"
