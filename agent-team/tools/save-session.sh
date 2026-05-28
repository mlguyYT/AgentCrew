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
  printf '%s\n' "  --tried TEXT         Failed approach worth remembering. May be repeated"
  printf '%s\n' "  --risk TEXT          Open risk or uncertainty. May be repeated"
  printf '%s\n' "  --skill TEXT         Role or Skill used. May be repeated"
  printf '%s\n' "  --validation TEXT    Validation evidence or baseline. May be repeated"
  printf '%s\n' "  --checkpoint-block   Include an [agentcrew-context] block"
  printf '%s\n' "  --out-dir PATH       Output directory. Default: PROJECT_ROOT/.agent-state/sessions"
  printf '%s\n' "  -h, --help           Show help"
}

PROJECT="."
TITLE="session"
SUMMARY=""
OUT_DIR=""
DECISIONS=()
NEXT_STEPS=()
NOTES=()
TRIED=()
RISKS=()
SKILLS_USED=()
VALIDATIONS=()
CHECKPOINT_BLOCK="false"

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
    --tried)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --tried" >&2; exit 2; }
      TRIED+=("$2")
      CHECKPOINT_BLOCK="true"
      shift 2
      ;;
    --risk)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --risk" >&2; exit 2; }
      RISKS+=("$2")
      CHECKPOINT_BLOCK="true"
      shift 2
      ;;
    --skill)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --skill" >&2; exit 2; }
      SKILLS_USED+=("$2")
      CHECKPOINT_BLOCK="true"
      shift 2
      ;;
    --validation)
      [ "$#" -ge 2 ] || { printf '%s\n' "Missing value for --validation" >&2; exit 2; }
      VALIDATIONS+=("$2")
      CHECKPOINT_BLOCK="true"
      shift 2
      ;;
    --checkpoint-block)
      CHECKPOINT_BLOCK="true"
      shift
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

slugify() {
  printf '%s' "$1" |
    tr '[:upper:]' '[:lower:]' |
    tr -s '[:space:]' '-' |
    tr -cd 'a-z0-9.-' |
    cut -c1-60
}

PROJECT_INPUT="$PROJECT"
PROJECT_ABS="$(cd "$PROJECT_INPUT" && pwd -P)" || exit 1

is_git_repo="false"
PROJECT_ROOT="$PROJECT_ABS"
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  is_git_repo="true"
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

PROJECT_NAME="$(basename "$PROJECT_ROOT")"
PROJECT_ID="$(slugify "$PROJECT_NAME")"
PROJECT_ID="${PROJECT_ID:-project}"

# Refuse to write outside $HOME unless the project is a git worktree. This
# catches accidental `--project /etc` style invocations before they create
# .agent-state under a system directory (security review INFO-3).
case "$PROJECT_ROOT" in
  "$HOME"|"$HOME"/*) : ;;
  *)
    if [ "$is_git_repo" != "true" ]; then
      printf 'Refusing to write under %s: outside $HOME and not a git worktree.\n' "$PROJECT_ROOT" >&2
      printf 'Set --project to a path inside your home directory or inside a git repository.\n' >&2
      exit 1
    fi
    ;;
esac

if [ -z "$OUT_DIR" ]; then
  OUT_DIR="$PROJECT_ROOT/.agent-state/sessions"
fi

mkdir -p "$OUT_DIR" || exit 1

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

git_value() {
  if [ "$is_git_repo" = "true" ]; then
    git -C "$PROJECT_ROOT" "$@" 2>/dev/null || true
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

write_context_lines() {
  local label="$1"
  shift
  local item
  for item in "$@"; do
    printf '%s: %s\n' "$label" "$item"
  done
}

{
  printf '%s\n' '---'
  printf '%s\n' 'status: saved'
  printf 'timestamp: %s\n' "$ISO_TIMESTAMP"
  printf 'project: %s\n' "$PROJECT_NAME"
  printf 'project_id: %s\n' "$PROJECT_ID"
  printf '%s\n' 'project_root: omitted-team-neutral'
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
  if [ "${#TRIED[@]}" -gt 0 ]; then
    printf '\n## Tried\n\n'
    write_list "No failed approaches recorded." "${TRIED[@]}"
  fi
  if [ "${#RISKS[@]}" -gt 0 ]; then
    printf '\n## Risks\n\n'
    write_list "No risks recorded." "${RISKS[@]}"
  fi
  if [ "${#VALIDATIONS[@]}" -gt 0 ]; then
    printf '\n## Validation\n\n'
    write_list "No validation recorded." "${VALIDATIONS[@]}"
  fi
  if [ "$CHECKPOINT_BLOCK" = "true" ]; then
    printf '\n## AgentCrew Context Block\n\n```text\n'
    printf '%s\n' '[agentcrew-context]'
    printf 'Task: %s\n' "$TITLE"
    printf 'Status: saved\n'
    write_context_lines "Decision" "${DECISIONS[@]}"
    write_context_lines "Remaining" "${NEXT_STEPS[@]}"
    write_context_lines "Tried" "${TRIED[@]}"
    write_context_lines "Risk" "${RISKS[@]}"
    write_context_lines "Skill" "${SKILLS_USED[@]}"
    write_context_lines "Validation" "${VALIDATIONS[@]}"
    printf '%s\n' '[/agentcrew-context]'
    printf '```\n'
  fi
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
  printf '%s\n' 'This checkpoint intentionally avoids full diffs, raw logs, secrets, tokens, raw customer data, sensitive production data, personal identifiers, sensitive local paths, and workstation-specific auth commands.'
} > "$FILE"

SENSITIVE_PATTERN='[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}|/home/[^[:space:]]+|/Users/[^[:space:]]+|[A-Za-z]:\\Users\\|\.ssh/|id_rsa|id_ed25519|deploy[-_ ]?key'
if grep -Eiq "$SENSITIVE_PATTERN" "$FILE"; then
  rm -f "$FILE"
  printf '%s\n' 'Refusing to save session: generated checkpoint contains personal identifiers, private key paths, deploy-key paths, local machine paths, or workstation-specific auth details.' >&2
  printf '%s\n' 'Remove that content or keep it in private local notes, then rerun save-session.sh.' >&2
  exit 1
fi

printf '%s\n' "AGENTCREW SESSION SAVED"
printf '%s\n' "File: $FILE"
printf '%s\n' "Project: $PROJECT_NAME"
printf '%s\n' "Project root: $PROJECT_ROOT"
if [ "$is_git_repo" = "true" ]; then
  printf '%s\n' "Branch: ${BRANCH:-unknown}"
  printf '%s\n' "Head: ${HEAD_SHA:-unknown}"
fi
