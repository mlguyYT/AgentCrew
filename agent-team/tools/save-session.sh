#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: save-session.sh [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --project PATH       Target project path. Default: current directory"
  printf '%s\n' "  --title TEXT         Session title. Default: session"
  printf '%s\n' "  --summary TEXT       Short summary of current work"
  printf '%s\n' "  --decision TEXT      Decision to save. May be repeated"
  printf '%s\n' "  --next TEXT          Next step to save. May be repeated"
  printf '%s\n' "  --note TEXT          Note to save. May be repeated"
  printf '%s\n' "  --out-dir PATH       Output directory. Default: PROJECT/.agent-state/sessions"
  printf '%s\n' "  -h, --help           Show help"
}

PROJECT="."
TITLE="session"
SUMMARY=""
OUT_DIR=""
DECISIONS=()
NEXT_STEPS=()
NOTES=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --project" >&2; exit 2; }
      PROJECT="$2"
      shift 2
      ;;
    --title)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --title" >&2; exit 2; }
      TITLE="$2"
      shift 2
      ;;
    --summary)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --summary" >&2; exit 2; }
      SUMMARY="$2"
      shift 2
      ;;
    --decision)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --decision" >&2; exit 2; }
      DECISIONS+=("$2")
      shift 2
      ;;
    --next)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --next" >&2; exit 2; }
      NEXT_STEPS+=("$2")
      shift 2
      ;;
    --note)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --note" >&2; exit 2; }
      NOTES+=("$2")
      shift 2
      ;;
    --out-dir)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --out-dir" >&2; exit 2; }
      OUT_DIR="$2"
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

if [ -z "$OUT_DIR" ]; then
  OUT_DIR="$PROJECT/.agent-state/sessions"
fi

mkdir -p "$OUT_DIR" || exit 1

slugify() {
  printf '%s' "$1" |
    tr '[:upper:]' '[:lower:]' |
    tr -s '[:space:]' '-' |
    tr -cd 'a-z0-9.-' |
    cut -c1-60
}

TITLE_SLUG="$(slugify "$TITLE")"
TITLE_SLUG="${TITLE_SLUG:-session}"
TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
ISO_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
FILE="$OUT_DIR/${TIMESTAMP}-${TITLE_SLUG}.md"

if [ -e "$FILE" ]; then
  SUFFIX="$(LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom 2>/dev/null | head -c 4)"
  SUFFIX="${SUFFIX:-$$}"
  FILE="$OUT_DIR/${TIMESTAMP}-${TITLE_SLUG}-${SUFFIX}.md"
fi

is_git_repo="false"
if git -C "$PROJECT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  is_git_repo="true"
fi

git_value() {
  if [ "$is_git_repo" = "true" ]; then
    git -C "$PROJECT" "$@" 2>/dev/null || true
  fi
}

BRANCH="$(git_value rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" = "HEAD" ]; then
  BRANCH="$(git_value symbolic-ref --short HEAD)"
fi
HEAD_SHA="$(git_value rev-parse --short HEAD)"
STATUS="$(git_value status --short)"
DIFF_STAT="$(git_value diff --stat)"
STAGED_DIFF_STAT="$(git_value diff --cached --stat)"
RECENT_LOG="$(git_value log --oneline -10)"

if [ -z "$SUMMARY" ]; then
  SUMMARY="Session checkpoint saved by AgentCrew. Add details with --summary, --decision, --next, and --note."
fi

write_list() {
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

{
  printf '%s\n' '---'
  printf '%s\n' 'status: saved'
  printf 'timestamp: %s\n' "$ISO_TIMESTAMP"
  printf 'project: %s\n' "$PROJECT"
  printf 'git_repo: %s\n' "$is_git_repo"
  if [ -n "$BRANCH" ]; then
    printf 'branch: %s\n' "$BRANCH"
  fi
  if [ -n "$HEAD_SHA" ]; then
    printf 'head: %s\n' "$HEAD_SHA"
  fi
  printf '%s\n' '---'
  printf '%s\n\n' ""
  printf '# Session: %s\n\n' "$TITLE"
  printf '## Summary\n\n%s\n\n' "$SUMMARY"
  printf '## Decisions\n\n'
  write_list "No decisions recorded." "${DECISIONS[@]}"
  printf '\n## Next Steps\n\n'
  write_list "No next steps recorded." "${NEXT_STEPS[@]}"
  printf '\n## Notes\n\n'
  write_list "No notes recorded." "${NOTES[@]}"
  printf '\n## Git State\n\n'
  if [ "$is_git_repo" = "true" ]; then
    printf -- '- branch: %s\n' "${BRANCH:-unknown}"
    printf -- '- head: %s\n' "${HEAD_SHA:-unknown}"
  else
    printf -- '- not a git repository\n'
  fi
  printf '\n### Status\n\n```text\n%s\n```\n\n' "${STATUS:-clean or unavailable}"
  printf '### Diff Stat\n\n```text\n%s\n```\n\n' "${DIFF_STAT:-none}"
  printf '### Staged Diff Stat\n\n```text\n%s\n```\n\n' "${STAGED_DIFF_STAT:-none}"
  printf '### Recent Log\n\n```text\n%s\n```\n\n' "${RECENT_LOG:-unavailable}"
  printf '## Safety\n\n'
  printf '%s\n' 'This checkpoint intentionally avoids full diffs, raw logs, secrets, tokens, raw customer data, and sensitive production data.'
} > "$FILE"

printf '%s\n' "AGENTCREW SESSION SAVED"
printf '%s\n' "File: $FILE"
printf '%s\n' "Project: $PROJECT"
if [ "$is_git_repo" = "true" ]; then
  printf '%s\n' "Branch: ${BRANCH:-unknown}"
  printf '%s\n' "Head: ${HEAD_SHA:-unknown}"
fi
