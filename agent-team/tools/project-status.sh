#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: project-status.sh [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --project PATH       Target project path. Default: current directory"
  printf '%s\n' "  -h, --help           Show help"
}

PROJECT="."

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --project" >&2; exit 2; }
      PROJECT="$2"
      shift 2
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

STATE_DIR="$PROJECT_ROOT/.agent-state"

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

first_pending_decision() {
  local file="$1"
  [ -f "$file" ] || return 1
  awk '
    /^## Pending Decisions/ { in_pending = 1; next }
    in_pending && /^## / { exit }
    in_pending && /^### / { sub(/^### /, ""); print; exit }
  ' "$file"
}

file_status() {
  local label="$1"
  local file="$2"
  if [ -f "$file" ]; then
    local title
    title="$(first_heading "$file")"
    [ -n "$title" ] || title="present"
    printf '  - %s: %s\n' "$label" "$title"
  else
    printf '  - %s: not set\n' "$label"
  fi
}

print_value() {
  local label="$1"
  local value="$2"
  [ -n "$value" ] || value="not set"
  printf '  - %s: %s\n' "$label" "$value"
}

printf '%s\n' "Project Dashboard"
printf '%s\n' ""
printf '%s\n' "Project"
printf '  - name: %s\n' "$(basename "$PROJECT_ROOT")"
printf '  - git_repo: %s\n' "$IS_GIT_REPO"
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
  STATUS_SHORT="$(git -C "$PROJECT_ROOT" status --short 2>/dev/null || true)"
  if [ -z "$STATUS_SHORT" ]; then
    WORKTREE="clean"
  else
    WORKTREE="changes present"
  fi
  print_value "current_branch" "$BRANCH"
  print_value "default_branch" "$DEFAULT_BRANCH"
  print_value "head" "$HEAD_SHA"
  print_value "worktree" "$WORKTREE"
else
  print_value "current_branch" "unknown"
  print_value "default_branch" "unknown"
  print_value "head" "unknown"
  print_value "worktree" "not a git repository"
fi

printf '%s\n' ""
printf '%s\n' "AgentCrew State"
if [ -d "$STATE_DIR" ]; then
  printf '  - state_dir: present\n'
else
  printf '  - state_dir: not found\n'
fi

CURRENT_TASK="$STATE_DIR/current-task.md"
printf '%s\n' ""
printf '%s\n' "Current Task"
if [ -f "$CURRENT_TASK" ]; then
  TITLE="$(section_value "$CURRENT_TASK" "Title")"
  LANE="$(section_value "$CURRENT_TASK" "Lane")"
  RISK="$(section_value "$CURRENT_TASK" "Risk")"
  QUALITY_PROFILE="$(section_value "$CURRENT_TASK" "Quality Profile")"
  RECIPE="$(section_value "$CURRENT_TASK" "Recipe")"
  OWNER="$(section_value "$CURRENT_TASK" "Owner")"
  STATUS="$(section_value "$CURRENT_TASK" "Status")"
  NEXT_ACTION="$(section_value "$CURRENT_TASK" "Next Action")"
  print_value "title" "$TITLE"
  print_value "lane" "$LANE"
  print_value "risk" "$RISK"
  print_value "quality_profile" "$QUALITY_PROFILE"
  print_value "recipe" "$RECIPE"
  print_value "owner" "$OWNER"
  print_value "status" "$STATUS"
  print_value "next_action" "$NEXT_ACTION"
else
  printf '  - current-task.md: not set\n'
fi

printf '%s\n' ""
printf '%s\n' "Reports"
file_status "test" "$STATE_DIR/test-report.md"
file_status "review" "$STATE_DIR/review-report.md"
file_status "security" "$STATE_DIR/security-review-report.md"
file_status "ux_design" "$STATE_DIR/ux-design-review-report.md"
file_status "documentation" "$STATE_DIR/documentation-report.md"
file_status "support_triage" "$STATE_DIR/support-triage-report.md"
file_status "release" "$STATE_DIR/release-report.md"

printf '%s\n' ""
printf '%s\n' "Memory And Decisions"
file_status "project_preset" "$STATE_DIR/project-preset.md"
file_status "task_brief" "$STATE_DIR/task-brief.md"
file_status "work_plan" "$STATE_DIR/work-plan.md"
file_status "readiness" "$STATE_DIR/readiness-report.md"
file_status "pr_pack" "$STATE_DIR/pr-pack.md"
file_status "decisions" "$STATE_DIR/decisions.md"
file_status "handoff" "$STATE_DIR/handoff.md"
file_status "memory" "$STATE_DIR/memory.md"

printf '%s\n' ""
printf '%s\n' "Latest Session"
SESSIONS_DIR="$STATE_DIR/sessions"
if [ -d "$SESSIONS_DIR" ]; then
  LATEST="$(find "$SESSIONS_DIR" -maxdepth 1 -type f -name '*.md' -print 2>/dev/null | sort | tail -n 1)"
  if [ -n "$LATEST" ]; then
    SESSION_TITLE="$(sed -n 's/^# Session: //p' "$LATEST" | head -n 1)"
    SESSION_TIME="$(sed -n 's/^timestamp: //p' "$LATEST" | head -n 1)"
    [ -n "$SESSION_TITLE" ] || SESSION_TITLE="$(basename "$LATEST" .md)"
    print_value "title" "$SESSION_TITLE"
    print_value "timestamp" "$SESSION_TIME"
    printf '  - file: %s\n' "$(basename "$LATEST")"
  else
    printf '  - latest: no saved sessions\n'
  fi
else
  printf '  - latest: no sessions directory\n'
fi

printf '%s\n' ""
printf '%s\n' "Human Attention"
HUMAN_DECISIONS="$STATE_DIR/human-decisions.md"
if [ -f "$HUMAN_DECISIONS" ]; then
  PENDING_DECISION="$(first_pending_decision "$HUMAN_DECISIONS")"
  print_value "decision_queue" "present"
  print_value "first_pending_decision" "$PENDING_DECISION"
else
  print_value "decision_queue" "not set"
fi
if [ -f "$CURRENT_TASK" ]; then
  OPEN_QUESTIONS="$(section_value "$CURRENT_TASK" "Open Questions")"
  print_value "open_questions" "$OPEN_QUESTIONS"
else
  printf '  - open_questions: not set\n'
fi
printf '  - reminder: human approval remains final for product direction, risk acceptance, PR approval, and merge\n'
