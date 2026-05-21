#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: select-preset.sh [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --project PATH      Target project path. Default: current directory"
  printf '%s\n' "  --force             Overwrite existing .agent-state/project-preset.md"
  printf '%s\n' "  --dry-run           Print the project preset without writing"
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
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

PROJECT_NAME="$(basename "$PROJECT_ROOT")"
STATE_DIR="$PROJECT_ROOT/.agent-state"
PRESET_FILE="$STATE_DIR/project-preset.md"

has_file() {
  [ -f "$PROJECT_ROOT/$1" ]
}

has_dir() {
  [ -d "$PROJECT_ROOT/$1" ]
}

find_files() {
  find "$PROJECT_ROOT" \
    -path "$PROJECT_ROOT/.git" -prune -o \
    -path "$PROJECT_ROOT/node_modules" -prune -o \
    -path "$PROJECT_ROOT/vendor" -prune -o \
    -path "$PROJECT_ROOT/.venv" -prune -o \
    -path "$PROJECT_ROOT/venv" -prune -o \
    -path "$PROJECT_ROOT/dist" -prune -o \
    -path "$PROJECT_ROOT/build" -prune -o \
    -path "$PROJECT_ROOT/target" -prune -o \
    -type f "$@" -print 2>/dev/null
}

has_ext() {
  local pattern="$1"
  find_files -name "$pattern" | head -n 1 | grep -q .
}

file_mentions() {
  local file="$1"
  local pattern="$2"
  [ -f "$PROJECT_ROOT/$file" ] && grep -Eiq "$pattern" "$PROJECT_ROOT/$file"
}

SIGNALS=()
SKILLS=()
VALIDATION=()
GATES=()
ARCHITECTURE=()
PRESET="unknown"
CONFIDENCE="low"
NEXT_ACTION="Use project detection and repository inspection before selecting detailed Skills."

add_unique() {
  local array_name="$1"
  local value="$2"
  eval 'local existing="${'"$array_name"'[*]-}"'
  case " $existing " in
    *" $value "*) ;;
    *) eval "$array_name+=(\"\$value\")" ;;
  esac
}

select_react_frontend() {
  PRESET="react_frontend"
  CONFIDENCE="high"
  add_unique SIGNALS "React, Next.js, or Vite dependency detected"
  add_unique SKILLS "typescript-pro when TypeScript is present"
  add_unique SKILLS "react"
  add_unique VALIDATION "package-manager test command when available"
  add_unique VALIDATION "lint, typecheck, and build commands when available"
  add_unique VALIDATION "coverage gate when coverage tooling exists"
  add_unique GATES "UX / Design Reviewer for user-facing flow, accessibility, layout, or responsive changes"
  add_unique GATES "Reviewer for shared components, routing, or state-management changes"
  add_unique GATES "Security Reviewer for auth, tokens, customer data, dependencies, or runtime config"
  add_unique ARCHITECTURE "separate presentation, state, data fetching, and routing concerns"
  add_unique ARCHITECTURE "keep components small, composable, accessible, and responsive"
  NEXT_ACTION="Load agent-team/presets/react-frontend.md plus matching Skills before implementation."
}

select_python_api() {
  PRESET="python_api"
  CONFIDENCE="high"
  add_unique SIGNALS "Python API framework or Python package metadata detected"
  add_unique SKILLS "python-pro"
  add_unique SKILLS "fastapi when FastAPI is detected"
  add_unique SKILLS "sql-pro when persistence or migrations are touched"
  add_unique VALIDATION "pytest when available"
  add_unique VALIDATION "ruff or equivalent lint command when available"
  add_unique VALIDATION "mypy or type checking when configured"
  add_unique VALIDATION "coverage gate when coverage tooling exists"
  add_unique GATES "Security Reviewer for auth, permissions, secrets, data, dependencies, or production config"
  add_unique GATES "Reviewer for API contracts, shared services, migrations, or behavior-changing refactors"
  add_unique GATES "Documentation Agent when public API behavior or examples change"
  add_unique ARCHITECTURE "separate routing, business logic, persistence, and external integrations"
  add_unique ARCHITECTURE "validate request and response boundaries explicitly"
  NEXT_ACTION="Load agent-team/presets/python-api.md plus matching Skills before implementation."
}

select_node_service() {
  PRESET="node_service"
  CONFIDENCE="high"
  add_unique SIGNALS "Node API dependency or server-side package metadata detected"
  add_unique SKILLS "typescript-pro when TypeScript is present"
  add_unique SKILLS "javascript-pro"
  add_unique SKILLS "sql-pro when persistence or migrations are touched"
  add_unique VALIDATION "package-manager test command when available"
  add_unique VALIDATION "lint, typecheck, and build commands when available"
  add_unique VALIDATION "audit command when dependencies or lockfiles change"
  add_unique GATES "Security Reviewer for auth, data, dependencies, runtime, or production config"
  add_unique GATES "Reviewer for public API behavior, shared modules, async flow, or refactors"
  add_unique GATES "Documentation Agent when public API behavior or examples change"
  add_unique ARCHITECTURE "separate handlers, domain logic, persistence, and external clients"
  add_unique ARCHITECTURE "preserve protocol and API contracts unless behavior change is explicit"
  NEXT_ACTION="Load agent-team/presets/node-service.md plus matching Skills before implementation."
}

select_cli_tool() {
  PRESET="cli_tool"
  CONFIDENCE="medium"
  add_unique SIGNALS "shell, bin directory, Makefile, or CLI package metadata detected"
  add_unique SKILLS "shell-pro for shell entrypoints and install scripts"
  add_unique SKILLS "language-specific Skills from registry"
  add_unique VALIDATION "command help output works"
  add_unique VALIDATION "shell syntax checks for shell scripts"
  add_unique VALIDATION "dry-run path tested when available"
  add_unique GATES "Reviewer for destructive operations, filesystem writes, install behavior, or generated artifacts"
  add_unique GATES "Security Reviewer for credentials, shell execution, downloads, or supply-chain changes"
  add_unique ARCHITECTURE "separate command parsing, execution, and output formatting"
  add_unique ARCHITECTURE "make dry-run and force semantics explicit for write operations"
  NEXT_ACTION="Load agent-team/presets/cli-tool.md plus matching Skills before implementation."
}

select_general_library() {
  PRESET="general_library"
  CONFIDENCE="medium"
  add_unique SIGNALS "language or package metadata detected without a dominant app framework"
  add_unique SKILLS "language-specific Skills from registry"
  add_unique VALIDATION "package test command when available"
  add_unique VALIDATION "compile, typecheck, or lint command when configured"
  add_unique VALIDATION "coverage gate when coverage tooling exists"
  add_unique GATES "Reviewer for public API, shared-module, or behavior-changing refactors"
  add_unique GATES "Documentation Agent for README, examples, changelog, or public API behavior changes"
  add_unique GATES "Security Reviewer for dependency, build, release, or supply-chain changes"
  add_unique ARCHITECTURE "keep public API stable and documented"
  add_unique ARCHITECTURE "preserve exported symbols, data shapes, schemas, and compatibility-sensitive behavior"
  NEXT_ACTION="Load agent-team/presets/general-library.md plus matching Skills before implementation."
}

# Selection order: more specific app shapes first.
if has_file package.json && file_mentions package.json '"react"|"next"|"@vitejs/plugin-react"'; then
  select_react_frontend
elif { has_file pyproject.toml || has_file requirements.txt; } && { file_mentions pyproject.toml 'fastapi|django|flask' || file_mentions requirements.txt 'fastapi|django|flask'; }; then
  select_python_api
elif has_file package.json && file_mentions package.json '"express"|"fastify"|"nestjs"|"@nestjs/'; then
  select_node_service
elif has_dir bin || has_ext '*.sh' || has_file Makefile; then
  select_cli_tool
elif has_file package.json || has_file pyproject.toml || has_file requirements.txt || has_file go.mod || has_file Cargo.toml || has_file composer.json || has_ext '*.csproj' || has_ext '*.sln' || has_file pom.xml || has_file build.gradle || has_file build.gradle.kts; then
  select_general_library
else
  add_unique SIGNALS "no strong preset signal detected"
  add_unique SKILLS "inspect repository and load matching Skills from registry"
  add_unique VALIDATION "discover project validation commands before implementation"
  add_unique GATES "Reviewer when risk is meaningful"
  add_unique ARCHITECTURE "follow existing project architecture and keep changes modular"
fi

# Cross-cutting platform hints.
if has_file Dockerfile || has_file docker-compose.yml || has_file compose.yml; then
  add_unique SIGNALS "container files detected"
  add_unique GATES "Supply-chain and runtime gate when container or runtime files change"
fi
if has_dir .github/workflows || has_file .gitlab-ci.yml || has_file Jenkinsfile; then
  add_unique SIGNALS "CI/CD files detected"
  add_unique GATES "Reviewer for CI/CD behavior and default-branch merge readiness"
fi
if find_files -name '*.sql' | head -n 1 | grep -q .; then
  add_unique SKILLS "sql-pro when SQL changes are in scope"
  add_unique GATES "Reviewer for migrations, schema changes, and data compatibility"
fi

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

artifact() {
  printf '# Project Preset\n\n'
  printf '## Preset\n%s\n\n' "$PRESET"
  printf '## Project\n%s\n\n' "$PROJECT_NAME"
  printf '## Confidence\n%s\n\n' "$CONFIDENCE"
  printf '## Signals\n'
  print_list "None" "${SIGNALS[@]}"
  printf '\n## Default Skills\n'
  print_list "Inspect repository and load matching Skills from registry" "${SKILLS[@]}"
  printf '\n## Validation Defaults\n'
  print_list "Discover validation commands before implementation" "${VALIDATION[@]}"
  printf '\n## Review Gates\n'
  print_list "Reviewer when risk is meaningful" "${GATES[@]}"
  printf '\n## Architecture Focus\n'
  print_list "Follow existing project architecture and keep changes modular" "${ARCHITECTURE[@]}"
  printf '\n## Next Action\n%s\n\n' "$NEXT_ACTION"
  printf '## Handoff\n\n'
  printf '### Context\n'
  printf -- '- Project preset selected from project-local structure and package signals.\n\n'
  printf '### Decision\n'
  printf 'Selected preset: %s (%s confidence).\n\n' "$PRESET" "$CONFIDENCE"
  printf '### Evidence\n'
  print_list "No strong signal detected" "${SIGNALS[@]}"
  printf '\n### Next Action\n%s\n\n' "$NEXT_ACTION"
  printf '### Open Questions\n'
  if [ "$PRESET" = "unknown" ]; then
    printf -- '- Confirm project shape before relying on preset guidance.\n'
  else
    printf -- '- None detected.\n'
  fi
}

if [ "$DRY_RUN" = "true" ]; then
  artifact
  exit 0
fi

if [ -f "$PRESET_FILE" ] && [ "$FORCE" != "true" ]; then
  printf '%s\n' "Refusing to overwrite existing project preset: $PRESET_FILE" >&2
  printf '%s\n' "Use --force to replace it." >&2
  exit 1
fi

mkdir -p "$STATE_DIR" || exit 1
artifact > "$PRESET_FILE" || exit 1

SENSITIVE_PATTERN='[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}|/home/[^[:space:]]+|/Users/[^[:space:]]+|[A-Za-z]:\\Users\\|\.ssh/|id_rsa|id_ed25519|deploy[-_ ]?key'
if grep -Eiq "$SENSITIVE_PATTERN" "$PRESET_FILE"; then
  rm -f "$PRESET_FILE"
  printf '%s\n' 'Refusing to save project preset: generated artifact contains personal identifiers, private key paths, deploy-key paths, or local machine paths.' >&2
  exit 1
fi

printf '%s\n' "AGENTCREW PROJECT PRESET COMPLETE"
printf '%s\n' "File: $PRESET_FILE"
printf '%s\n' "Preset: $PRESET"
printf '%s\n' "Confidence: $CONFIDENCE"
