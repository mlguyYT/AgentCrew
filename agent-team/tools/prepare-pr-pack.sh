#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: prepare-pr-pack.sh [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --project PATH      Target project path. Default: current directory"
  printf '%s\n' "  --force             Overwrite existing .agent-state/pr-pack.md"
  printf '%s\n' "  --dry-run           Print the PR packet without writing"
  printf '%s\n' "  -h, --help          Show help"
}

PROJECT="."
FORCE="false"
DRY_RUN="false"

while [ "$#" -gt 0 ]; do
  case "$1" in
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
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ ! -d "$PROJECT" ]; then
  printf 'Project path does not exist: %s\n' "$PROJECT" >&2
  exit 1
fi

PROJECT_ABS="$(cd "$PROJECT" && pwd -P)" || exit 1
PROJECT_ROOT="$PROJECT_ABS"
IS_GIT_REPO="false"
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  IS_GIT_REPO="true"
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

# Refuse to write outside $HOME unless the project is a git worktree
# (security review INFO-3).
case "$PROJECT_ROOT" in
  "$HOME"|"$HOME"/*) ;;
  *)
    if [ "$IS_GIT_REPO" != "true" ]; then
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
READINESS_REPORT="$STATE_DIR/readiness-report.md"
TEST_REPORT="$STATE_DIR/test-report.md"
REVIEW_REPORT="$STATE_DIR/review-report.md"
SECURITY_REPORT="$STATE_DIR/security-review-report.md"
UX_REPORT="$STATE_DIR/ux-design-review-report.md"
DOC_REPORT="$STATE_DIR/documentation-report.md"
ARCHITECTURE_REPORT="$STATE_DIR/architecture-report.md"
HUMAN_DECISIONS="$STATE_DIR/human-decisions.md"
PR_PACK="$STATE_DIR/pr-pack.md"

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

first_heading() {
  local file="$1"
  [ -f "$file" ] || return 1
  sed -n 's/^# //p' "$file" | head -n 1
}

file_state() {
  local file="$1"
  if [ -f "$file" ]; then
    local title
    title="$(first_heading "$file")"
    [ -n "$title" ] || title="present"
    printf '%s' "$title"
  else
    printf '%s' "missing"
  fi
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

first_pending_decision() {
  local file="$1"
  [ -f "$file" ] || return 1
  awk '
    /^## Pending Decisions/ { in_pending = 1; next }
    in_pending && /^## / { exit }
    in_pending && /^### / { sub(/^### /, ""); print; exit }
  ' "$file"
}

print_list() {
  local empty_text="$1"
  shift
  if [ "$#" -eq 0 ]; then
    printf -- '- %s\n' "$empty_text"
    return
  fi
  local item
  for item in "$@"; do
    printf -- '- %s\n' "$item"
  done
}

BRANCH="unknown"
DEFAULT_BRANCH="unknown"
HEAD_SHA="unknown"
WORKTREE="not a git repository"
if [ "$IS_GIT_REPO" = "true" ]; then
  BRANCH="$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  HEAD_SHA="$(git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || true)"
  DEFAULT_BRANCH="$(git -C "$PROJECT_ROOT" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
  if [ -z "$DEFAULT_BRANCH" ]; then
    if git -C "$PROJECT_ROOT" show-ref --verify --quiet refs/heads/main; then
      DEFAULT_BRANCH="main"
    elif git -C "$PROJECT_ROOT" show-ref --verify --quiet refs/heads/master; then
      DEFAULT_BRANCH="master"
    else
      DEFAULT_BRANCH="unknown"
    fi
  fi
  if [ -z "$(git -C "$PROJECT_ROOT" status --short 2>/dev/null || true)" ]; then
    WORKTREE="clean"
  else
    WORKTREE="changes present"
  fi
fi

TITLE="$(section_value "$CURRENT_TASK" "Title")"
LANE="$(section_value "$CURRENT_TASK" "Lane")"
RISK="$(section_value "$CURRENT_TASK" "Risk")"
QUALITY_PROFILE="$(section_value "$CURRENT_TASK" "Quality Profile")"
RECIPE="$(section_value "$CURRENT_TASK" "Recipe")"
OWNER="$(section_value "$CURRENT_TASK" "Owner")"
ACCEPTANCE="$(section_value "$CURRENT_TASK" "Acceptance Criteria")"
READINESS_STATUS="$(section_value "$READINESS_REPORT" "Status")"
TEST_RESULT="$(section_value "$TEST_REPORT" "Result")"
COVERAGE="$(section_value "$TEST_REPORT" "Coverage")"
REVIEW_STATUS="$(section_value "$REVIEW_REPORT" "Status")"

[ -n "$TITLE" ] || TITLE="not set"
[ -n "$LANE" ] || LANE="unknown"
[ -n "$RISK" ] || RISK="unknown"
[ -n "$QUALITY_PROFILE" ] || QUALITY_PROFILE="unknown"
[ -n "$RECIPE" ] || RECIPE="unknown"
[ -n "$OWNER" ] || OWNER="unknown"
[ -n "$READINESS_STATUS" ] || READINESS_STATUS="not checked"
[ -n "$TEST_RESULT" ] || TEST_RESULT="not set"
[ -n "$COVERAGE" ] || COVERAGE="not set"
[ -n "$REVIEW_STATUS" ] || REVIEW_STATUS="not set"

BLOCKERS=()
WARNINGS=()
STATUS="draft"
NEXT_ACTION="Complete missing validation or review evidence before human approval."

if [ ! -f "$CURRENT_TASK" ]; then
  BLOCKERS+=("current task is missing")
fi

if [ "$READINESS_STATUS" = "not_ready" ]; then
  BLOCKERS+=("implementation readiness is not ready")
elif [ ! -f "$READINESS_REPORT" ]; then
  WARNINGS+=("readiness report is missing")
fi

if has_pending_decision "$HUMAN_DECISIONS"; then
  BLOCKERS+=("pending human-only decision exists: $(first_pending_decision "$HUMAN_DECISIONS")")
fi

if [ ! -f "$TEST_REPORT" ]; then
  WARNINGS+=("test report is missing or validation gap is undocumented")
fi

if [ ! -f "$REVIEW_REPORT" ] && { [ "$RISK" = "medium" ] || [ "$RISK" = "high" ] || [ "$RISK" = "critical" ] || [ "$LANE" = "Full Lane" ]; }; then
  WARNINGS+=("review report is recommended for this risk or lane")
fi

if [ "${#BLOCKERS[@]}" -gt 0 ]; then
  STATUS="blocked"
  NEXT_ACTION="Resolve blocking issues before human PR approval."
elif [ -f "$TEST_REPORT" ] && { [ -f "$REVIEW_REPORT" ] || [ "$RISK" = "low" ]; }; then
  STATUS="ready_for_human_review"
  NEXT_ACTION="Human reviews the packet, accepts or rejects pending risk, then approves or requests changes."
fi

artifact() {
  printf '# PR Pack\n\n'
  printf '## Status\n%s\n\n' "$STATUS"
  printf '## Project Snapshot\n'
  printf -- '- project: %s\n' "$PROJECT_NAME"
  printf -- '- branch: %s\n' "$BRANCH"
  printf -- '- default_branch: %s\n' "$DEFAULT_BRANCH"
  printf -- '- head: %s\n' "$HEAD_SHA"
  printf -- '- worktree: %s\n\n' "$WORKTREE"
  printf '## Route Snapshot\n'
  printf -- '- title: %s\n' "$TITLE"
  printf -- '- lane: %s\n' "$LANE"
  printf -- '- risk: %s\n' "$RISK"
  printf -- '- quality_profile: %s\n' "$QUALITY_PROFILE"
  printf -- '- recipe: %s\n' "$RECIPE"
  printf -- '- owner: %s\n\n' "$OWNER"
  printf '## Artifact Status\n'
  printf -- '- current_task: %s\n' "$(file_state "$CURRENT_TASK")"
  printf -- '- task_brief: %s\n' "$(file_state "$TASK_BRIEF")"
  printf -- '- work_plan: %s\n' "$(file_state "$WORK_PLAN")"
  printf -- '- readiness_report: %s\n' "$(file_state "$READINESS_REPORT")"
  printf -- '- test_report: %s\n' "$(file_state "$TEST_REPORT")"
  printf -- '- review_report: %s\n' "$(file_state "$REVIEW_REPORT")"
  printf -- '- architecture_report: %s\n' "$(file_state "$ARCHITECTURE_REPORT")"
  printf -- '- security_review_report: %s\n' "$(file_state "$SECURITY_REPORT")"
  printf -- '- ux_design_review_report: %s\n' "$(file_state "$UX_REPORT")"
  printf -- '- documentation_report: %s\n' "$(file_state "$DOC_REPORT")"
  if has_pending_decision "$HUMAN_DECISIONS"; then
    printf -- '- human_decisions: pending\n\n'
  elif [ -f "$HUMAN_DECISIONS" ]; then
    printf -- '- human_decisions: clear\n\n'
  else
    printf -- '- human_decisions: not set\n\n'
  fi
  printf '## Validation Evidence\n'
  printf -- '- result: %s\n' "$TEST_RESULT"
  printf -- '- coverage: %s\n' "$COVERAGE"
  printf -- '- integration_tests: see test report when present\n\n'
  printf '## Review Evidence\n'
  printf -- '- reviewer: %s\n' "$REVIEW_STATUS"
  printf -- '- architecture: %s\n' "$(file_state "$ARCHITECTURE_REPORT")"
  printf -- '- security: %s\n' "$(file_state "$SECURITY_REPORT")"
  printf -- '- ux_design: %s\n' "$(file_state "$UX_REPORT")"
  printf -- '- documentation: %s\n\n' "$(file_state "$DOC_REPORT")"
  printf '## Human Decisions\n'
  if has_pending_decision "$HUMAN_DECISIONS"; then
    printf -- '- pending: %s\n' "$(first_pending_decision "$HUMAN_DECISIONS")"
    printf -- '- required_before_merge: yes\n\n'
  else
    printf -- '- pending: None detected\n'
    printf -- '- required_before_merge: human PR approval remains required\n\n'
  fi
  printf '## Risks And Gaps\n'
  printf '### Blocking\n'
  print_list "None" "${BLOCKERS[@]}"
  printf '\n### Non-Blocking\n'
  print_list "None" "${WARNINGS[@]}"
  printf '\n### Test Gaps\n'
  if [ -f "$TEST_REPORT" ]; then
    printf -- '- See test report.\n'
  else
    printf -- '- Test report missing.\n'
  fi
  printf '\n### Rollout Or Compatibility\n'
  printf -- '- See work plan, review report, or release notes when relevant.\n\n'
  printf '## Suggested PR Description\n\n'
  printf '### Summary\n'
  printf -- '- %s\n\n' "$TITLE"
  printf '### Acceptance Criteria\n'
  if [ -n "$ACCEPTANCE" ]; then
    printf -- '- [ ] %s\n\n' "$ACCEPTANCE"
  else
    printf -- '- [ ] Acceptance criteria documented in task brief or current task.\n\n'
  fi
  printf '### Tests\n'
  printf -- '- result: %s\n' "$TEST_RESULT"
  printf -- '- coverage: %s\n\n' "$COVERAGE"
  printf '### Review Notes\n'
  printf -- '- status: %s\n\n' "$STATUS"
  printf '### Human Approval Notes\n'
  printf -- '- Human approval is still required for PR approval, risk acceptance, and merge.\n\n'
  printf '## Handoff\n\n'
  printf '### Context\n'
  printf -- '- PR packet summarizes AgentCrew project-state artifacts for human review.\n\n'
  printf '### Decision\n'
  printf 'PR packet status: %s.\n\n' "$STATUS"
  printf '### Evidence\n'
  printf -- '- readiness: %s\n' "$READINESS_STATUS"
  printf -- '- test_report: %s\n' "$(file_state "$TEST_REPORT")"
  printf -- '- review_report: %s\n\n' "$(file_state "$REVIEW_REPORT")"
  printf '### Next Action\n'
  printf '%s\n\n' "$NEXT_ACTION"
  printf '### Open Questions\n'
  if [ "${#BLOCKERS[@]}" -gt 0 ]; then
    print_list "None" "${BLOCKERS[@]}"
  else
    printf -- '- None detected.\n'
  fi
}

if [ "$DRY_RUN" = "true" ]; then
  artifact
  exit 0
fi

if [ -f "$PR_PACK" ] && [ "$FORCE" != "true" ]; then
  printf '%s\n' "Refusing to overwrite existing PR packet: $PR_PACK" >&2
  printf '%s\n' "Use --force to replace it." >&2
  exit 1
fi

mkdir -p "$STATE_DIR" || exit 1
artifact > "$PR_PACK" || exit 1

SENSITIVE_PATTERN='[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}|/home/[^[:space:]]+|/Users/[^[:space:]]+|[A-Za-z]:\\Users\\|\.ssh/|id_rsa|id_ed25519|deploy[-_ ]?key'
if grep -Eiq "$SENSITIVE_PATTERN" "$PR_PACK"; then
  rm -f "$PR_PACK"
  printf '%s\n' 'Refusing to save PR packet: generated artifact contains personal identifiers, private key paths, deploy-key paths, or local machine paths.' >&2
  exit 1
fi

printf '%s\n' "AGENTCREW PR PACK COMPLETE"
printf '%s\n' "File: $PR_PACK"
printf '%s\n' "Status: $STATUS"
printf '%s\n' "Next action: $NEXT_ACTION"
