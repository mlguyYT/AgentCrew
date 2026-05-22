#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: restore-session.sh [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --project PATH       Target project path. Default: current directory"
  printf '%s\n' "  --out-dir PATH       Sessions directory. Default: PROJECT_ROOT/.agent-state/sessions"
  printf '%s\n' "  --file PATH          Restore a specific session file"
  printf '%s\n' "  -h, --help           Show help"
}

PROJECT="."
OUT_DIR=""
FILE=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --project" >&2; exit 2; }
      PROJECT="$2"
      shift 2
      ;;
    --out-dir)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --out-dir" >&2; exit 2; }
      OUT_DIR="$2"
      shift 2
      ;;
    --file)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --file" >&2; exit 2; }
      FILE="$2"
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
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

if [ -z "$OUT_DIR" ]; then
  OUT_DIR="$PROJECT_ROOT/.agent-state/sessions"
fi

if [ -n "$FILE" ]; then
  if [ ! -f "$FILE" ]; then
    printf 'Session file does not exist: %s\n' "$FILE" >&2
    exit 1
  fi
  SESSION_FILE="$FILE"
else
  if [ ! -d "$OUT_DIR" ]; then
    printf '%s\n' "No AgentCrew sessions found."
    printf '%s\n' "Project root: $PROJECT_ROOT"
    printf '%s\n' "Sessions dir: $OUT_DIR"
    exit 0
  fi
  SESSION_FILE="$(find "$OUT_DIR" -maxdepth 1 -type f -name '*.md' -print 2>/dev/null | sort | tail -n 1)"
  if [ -z "$SESSION_FILE" ]; then
    printf '%s\n' "No AgentCrew sessions found."
    printf '%s\n' "Project root: $PROJECT_ROOT"
    printf '%s\n' "Sessions dir: $OUT_DIR"
    exit 0
  fi
fi

frontmatter_value() {
  local key="$1"
  sed -n "s/^$key: //p" "$SESSION_FILE" | head -n 1
}

section() {
  local name="$1"
  awk -v header="## $name" '
    $0 == header { in_section = 1; next }
    in_section && /^## / { exit }
    in_section { print }
  ' "$SESSION_FILE" | sed '/^[[:space:]]*$/d'
}

context_block() {
  awk '
    $0 == "[agentcrew-context]" { in_block = 1; print; next }
    $0 == "[/agentcrew-context]" { print; exit }
    in_block { print }
  ' "$SESSION_FILE"
}

TITLE="$(sed -n 's/^# Session: //p' "$SESSION_FILE" | head -n 1)"
TIMESTAMP="$(frontmatter_value timestamp)"
BRANCH="$(frontmatter_value branch)"
HEAD_SHA="$(frontmatter_value head)"
SUMMARY="$(section Summary | sed -n '1,8p')"
DECISIONS="$(section Decisions | sed -n '1,8p')"
REMAINING="$(section 'Next Steps' | sed -n '1,10p')"
RISKS="$(section Risks | sed -n '1,8p')"
VALIDATION="$(section Validation | sed -n '1,8p')"
BLOCK="$(context_block)"

printf '%s\n' "AGENTCREW RESTORED SESSION"
printf '%s\n' "File: $SESSION_FILE"
printf '%s\n' "Project root: $PROJECT_ROOT"
printf '%s\n' "Title: ${TITLE:-unknown}"
printf '%s\n' "Saved: ${TIMESTAMP:-unknown}"
[ -n "$BRANCH" ] && printf '%s\n' "Branch: $BRANCH"
[ -n "$HEAD_SHA" ] && printf '%s\n' "Head: $HEAD_SHA"
printf '%s\n' ""

printf '%s\n' "## Summary"
printf '%s\n' "${SUMMARY:-No summary recorded.}"
printf '%s\n' ""
printf '%s\n' "## Decisions"
printf '%s\n' "${DECISIONS:-- No decisions recorded.}"
printf '%s\n' ""
printf '%s\n' "## Remaining Work"
printf '%s\n' "${REMAINING:-- No next steps recorded.}"
printf '%s\n' ""
if [ -n "$RISKS" ]; then
  printf '%s\n' "## Risks"
  printf '%s\n' "$RISKS"
  printf '%s\n' ""
fi
if [ -n "$VALIDATION" ]; then
  printf '%s\n' "## Validation"
  printf '%s\n' "$VALIDATION"
  printf '%s\n' ""
fi
if [ -n "$BLOCK" ]; then
  printf '%s\n' "## Checkpoint Block"
  printf '%s\n' '```text'
  printf '%s\n' "$BLOCK"
  printf '%s\n' '```'
  printf '%s\n' ""
fi
printf '%s\n' "Next action: continue with the first remaining work item, unless the human gives a newer direction."
