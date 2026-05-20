#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: detect-project.sh [options]"
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

unique_list() {
  printf '%s\n' "$@" | awk 'NF && !seen[$0]++'
}

join_unique() {
  unique_list "$@" | awk '
    BEGIN { first = 1 }
    {
      if (first == 1) {
        printf "%s", $0
        first = 0
      } else {
        printf ", %s", $0
      }
    }
    END { if (first == 0) printf "\n" }
  '
}

LANGUAGES=()
FRAMEWORKS=()
PACKAGE_MANAGERS=()
VALIDATION=()
COVERAGE=()
SKILLS=()
NOTES=()

# JavaScript and TypeScript
if has_file package.json || has_ext '*.js' || has_ext '*.jsx' || has_ext '*.mjs' || has_ext '*.cjs'; then
  LANGUAGES+=("JavaScript")
  SKILLS+=("javascript-pro")
fi
if has_file tsconfig.json || has_ext '*.ts' || has_ext '*.tsx'; then
  LANGUAGES+=("TypeScript")
  SKILLS+=("typescript-pro")
fi
if has_file package.json; then
  has_file pnpm-lock.yaml && PACKAGE_MANAGERS+=("pnpm")
  has_file yarn.lock && PACKAGE_MANAGERS+=("yarn")
  has_file package-lock.json && PACKAGE_MANAGERS+=("npm")
  has_file bun.lockb && PACKAGE_MANAGERS+=("bun")
  file_mentions package.json '"react"|"@vitejs/plugin-react"|"next"' && FRAMEWORKS+=("React") && SKILLS+=("react")
  file_mentions package.json '"next"' && FRAMEWORKS+=("Next.js")
  file_mentions package.json '"vite"' && FRAMEWORKS+=("Vite")
  file_mentions package.json '"vue"|"nuxt"' && FRAMEWORKS+=("Vue/Nuxt")
  file_mentions package.json '"svelte"|"@sveltejs/kit"' && FRAMEWORKS+=("Svelte/SvelteKit")
  file_mentions package.json '"express"|"fastify"|"nestjs"' && FRAMEWORKS+=("Node API")
  file_mentions package.json '"test"[[:space:]]*:' && VALIDATION+=("npm test or package-manager equivalent")
  file_mentions package.json '"lint"[[:space:]]*:' && VALIDATION+=("npm run lint or package-manager equivalent")
  file_mentions package.json '"build"[[:space:]]*:' && VALIDATION+=("npm run build or package-manager equivalent")
  file_mentions package.json '"coverage"[[:space:]]*:|"jest"|"vitest"|"nyc"|"c8"' && COVERAGE+=("JavaScript/TypeScript coverage tooling likely available")
fi

# Python
if has_file pyproject.toml || has_file requirements.txt || has_file setup.py || has_file setup.cfg || has_ext '*.py'; then
  LANGUAGES+=("Python")
  SKILLS+=("python-pro")
fi
has_file pyproject.toml && PACKAGE_MANAGERS+=("pyproject")
has_file poetry.lock && PACKAGE_MANAGERS+=("poetry")
has_file uv.lock && PACKAGE_MANAGERS+=("uv")
has_file requirements.txt && PACKAGE_MANAGERS+=("pip/requirements")
has_file Pipfile && PACKAGE_MANAGERS+=("pipenv")
if has_file pyproject.toml || has_file requirements.txt; then
  if file_mentions pyproject.toml 'fastapi' || file_mentions requirements.txt 'fastapi'; then
    FRAMEWORKS+=("FastAPI")
    SKILLS+=("fastapi")
  fi
  file_mentions pyproject.toml 'django' || file_mentions requirements.txt 'django' && FRAMEWORKS+=("Django")
  file_mentions pyproject.toml 'flask' || file_mentions requirements.txt 'flask' && FRAMEWORKS+=("Flask")
  file_mentions pyproject.toml 'pytest' || file_mentions requirements.txt 'pytest' && VALIDATION+=("pytest")
  file_mentions pyproject.toml 'ruff' || file_mentions requirements.txt 'ruff' && VALIDATION+=("ruff check")
  file_mentions pyproject.toml 'mypy' || file_mentions requirements.txt 'mypy' && VALIDATION+=("mypy")
  file_mentions pyproject.toml 'pytest-cov|coverage' || file_mentions requirements.txt 'pytest-cov|coverage' && COVERAGE+=("Python coverage tooling likely available")
fi

# Go
if has_file go.mod || has_ext '*.go'; then
  LANGUAGES+=("Go")
  SKILLS+=("go-pro")
  has_file go.mod && PACKAGE_MANAGERS+=("go modules")
  VALIDATION+=("go test ./...")
  COVERAGE+=("go test coverage can be enabled with -cover")
fi

# Rust
if has_file Cargo.toml || has_ext '*.rs'; then
  LANGUAGES+=("Rust")
  SKILLS+=("rust-pro")
  has_file Cargo.toml && PACKAGE_MANAGERS+=("cargo")
  VALIDATION+=("cargo test")
fi

# Java / Kotlin / Gradle / Maven
if has_file pom.xml || has_file build.gradle || has_file build.gradle.kts || has_ext '*.java' || has_ext '*.kt'; then
  LANGUAGES+=("Java/Kotlin")
  SKILLS+=("java-pro")
  has_file pom.xml && PACKAGE_MANAGERS+=("maven") && VALIDATION+=("mvn test")
  { has_file build.gradle || has_file build.gradle.kts; } && PACKAGE_MANAGERS+=("gradle") && VALIDATION+=("./gradlew test")
fi

# C# / .NET
if has_ext '*.csproj' || has_ext '*.sln' || has_ext '*.cs'; then
  LANGUAGES+=("C#/.NET")
  SKILLS+=("csharp-pro")
  PACKAGE_MANAGERS+=("dotnet/nuget")
  VALIDATION+=("dotnet test")
fi

# C / C++
if has_file CMakeLists.txt || has_ext '*.cpp' || has_ext '*.cc' || has_ext '*.cxx' || has_ext '*.hpp' || has_ext '*.h'; then
  LANGUAGES+=("C/C++")
  SKILLS+=("cpp-pro")
  has_file CMakeLists.txt && PACKAGE_MANAGERS+=("cmake")
fi

# PHP
if has_file composer.json || has_ext '*.php'; then
  LANGUAGES+=("PHP")
  SKILLS+=("php-pro")
  has_file composer.json && PACKAGE_MANAGERS+=("composer")
fi

# SQL and Shell
if has_ext '*.sql'; then
  LANGUAGES+=("SQL")
  SKILLS+=("sql-pro")
fi
if has_ext '*.sh' || has_file Makefile; then
  LANGUAGES+=("Shell/Make")
  SKILLS+=("shell-pro")
  has_file Makefile && VALIDATION+=("make test when available")
fi

# Platforms and project shape
if has_file Dockerfile || has_file docker-compose.yml || has_file compose.yml; then
  FRAMEWORKS+=("Containerized app")
fi
has_kubernetes_manifest() {
  local file
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    if grep -Eq 'apiVersion:[[:space:]]*(apps/|batch/|v1)|kind:[[:space:]]*(Deployment|Service|Ingress|ConfigMap|Secret|Job|CronJob)' "$file"; then
      return 0
    fi
  done <<EOF
$(find_files -name '*.yaml')
$(find_files -name '*.yml')
EOF
  return 1
}

if has_kubernetes_manifest; then
  FRAMEWORKS+=("Kubernetes")
  SKILLS+=("kubernetes")
fi
if has_dir .github/workflows || has_file .gitlab-ci.yml || has_file Jenkinsfile; then
  FRAMEWORKS+=("CI/CD")
fi
if has_file README.md; then
  NOTES+=("README.md exists")
else
  NOTES+=("README.md not detected")
fi
if has_dir docs; then
  NOTES+=("docs/ exists")
fi
if has_dir tests || has_dir test || find_files -path '*/__tests__/*' | head -n 1 | grep -q .; then
  NOTES+=("test directory detected")
else
  NOTES+=("test directory not detected")
fi

DEFAULT_BRANCH="unknown"
CURRENT_BRANCH="unknown"
HEAD_SHA="unknown"
if [ "$IS_GIT_REPO" = "true" ]; then
  CURRENT_BRANCH="$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
  HEAD_SHA="$(git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || printf 'unknown')"
  DEFAULT_BRANCH="$(git -C "$PROJECT_ROOT" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
  if [ -z "$DEFAULT_BRANCH" ]; then
    if git -C "$PROJECT_ROOT" show-ref --verify --quiet refs/heads/main; then
      DEFAULT_BRANCH="main"
    elif git -C "$PROJECT_ROOT" show-ref --verify --quiet refs/heads/master; then
      DEFAULT_BRANCH="master"
    else
      DEFAULT_BRANCH="$CURRENT_BRANCH"
    fi
  fi
fi

LANGUAGES_TEXT="$(join_unique "${LANGUAGES[@]}")"
FRAMEWORKS_TEXT="$(join_unique "${FRAMEWORKS[@]}")"
PACKAGE_TEXT="$(join_unique "${PACKAGE_MANAGERS[@]}")"
VALIDATION_TEXT="$(join_unique "${VALIDATION[@]}")"
COVERAGE_TEXT="$(join_unique "${COVERAGE[@]}")"
SKILLS_TEXT="$(join_unique "${SKILLS[@]}")"

[ -n "$LANGUAGES_TEXT" ] || LANGUAGES_TEXT="none detected"
[ -n "$FRAMEWORKS_TEXT" ] || FRAMEWORKS_TEXT="none detected"
[ -n "$PACKAGE_TEXT" ] || PACKAGE_TEXT="none detected"
[ -n "$VALIDATION_TEXT" ] || VALIDATION_TEXT="none detected"
[ -n "$COVERAGE_TEXT" ] || COVERAGE_TEXT="none detected"
[ -n "$SKILLS_TEXT" ] || SKILLS_TEXT="none detected"

printf '%s\n' "# AgentCrew Project Profile"
printf '%s\n' ""
printf '%s\n' "## Project"
printf '%s\n' ""
printf -- '- name: %s\n' "$(basename "$PROJECT_ROOT")"
printf -- '- git_repo: %s\n' "$IS_GIT_REPO"
printf -- '- current_branch: %s\n' "$CURRENT_BRANCH"
printf -- '- default_branch: %s\n' "$DEFAULT_BRANCH"
printf -- '- head: %s\n' "$HEAD_SHA"
printf '%s\n' ""
printf '%s\n' "## Detected Stack"
printf '%s\n' ""
printf -- '- languages: %s\n' "$LANGUAGES_TEXT"
printf -- '- frameworks: %s\n' "$FRAMEWORKS_TEXT"
printf -- '- package_managers: %s\n' "$PACKAGE_TEXT"
printf '%s\n' ""
printf '%s\n' "## Validation Hints"
printf '%s\n' ""
printf -- '- commands: %s\n' "$VALIDATION_TEXT"
printf -- '- coverage: %s\n' "$COVERAGE_TEXT"
printf '%s\n' ""
printf '%s\n' "## Suggested AgentCrew Skills"
printf '%s\n' ""
if [ "$SKILLS_TEXT" = "none detected" ]; then
  printf '%s\n' "- none detected"
else
  unique_list "${SKILLS[@]}" | sed 's/^/- /'
fi
printf '%s\n' ""
printf '%s\n' "## Notes"
printf '%s\n' ""
if [ "${#NOTES[@]}" -eq 0 ]; then
  printf '%s\n' "- none"
else
  unique_list "${NOTES[@]}" | sed 's/^/- /'
fi
printf '%s\n' ""
printf '%s\n' "## AgentCrew Use"
printf '%s\n' ""
printf '%s\n' "- Use this profile as a starting point, not as a substitute for inspecting the task and changed files."
printf '%s\n' "- Load only the Skills relevant to the current request."
printf '%s\n' "- Keep human approval final for product direction, risk acceptance, PR approval, and merge."
