#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: list-sessions.sh [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --project PATH       Target project path. Default: current directory"
  printf '%s\n' "  --out-dir PATH       Sessions directory. Default: PROJECT_ROOT/.agent-state/sessions"
  printf '%s\n' "  --latest            Print the latest saved session"
  printf '%s\n' "  -h, --help          Show help"
}

PROJECT="."
OUT_DIR=""
SHOW_LATEST="false"

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
    --latest)
      SHOW_LATEST="true"
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
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

if [ -z "$OUT_DIR" ]; then
  OUT_DIR="$PROJECT_ROOT/.agent-state/sessions"
fi

if [ ! -d "$OUT_DIR" ]; then
  printf '%s\n' "No AgentCrew sessions found."
  printf '%s\n' "Project root: $PROJECT_ROOT"
  printf '%s\n' "Sessions dir: $OUT_DIR"
  exit 0
fi

LATEST="$(find "$OUT_DIR" -maxdepth 1 -type f -name '*.md' -print 2>/dev/null | sort | tail -n 1)"

if [ -z "$LATEST" ]; then
  printf '%s\n' "No AgentCrew sessions found."
  printf '%s\n' "Project root: $PROJECT_ROOT"
  printf '%s\n' "Sessions dir: $OUT_DIR"
  exit 0
fi

if [ "$SHOW_LATEST" = "true" ]; then
  printf '%s\n' "AGENTCREW LATEST SESSION"
  printf '%s\n' "File: $LATEST"
  printf '%s\n' ""
  sed -n '1,240p' "$LATEST"
  exit 0
fi

printf '%s\n' "AGENTCREW SESSIONS"
printf '%s\n' "Project root: $PROJECT_ROOT"
printf '%s\n' "Sessions dir: $OUT_DIR"
printf '%s\n' ""

find "$OUT_DIR" -maxdepth 1 -type f -name '*.md' -print 2>/dev/null | sort | while IFS= read -r file; do
  title="$(sed -n 's/^# Session: //p' "$file" | head -n 1)"
  timestamp="$(sed -n 's/^timestamp: //p' "$file" | head -n 1)"
  [ -n "$title" ] || title="$(basename "$file" .md)"
  [ -n "$timestamp" ] || timestamp="unknown time"
  printf '%s | %s | %s\n' "$timestamp" "$title" "$file"
done
