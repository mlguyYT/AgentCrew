#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: context-manifest.sh --task TEXT [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --task TEXT         User request to route"
  printf '%s\n' "  --project PATH      Target project path. Default: current directory"
  printf '%s\n' "  -h, --help          Show help"
}

TASK=""
PROJECT="."
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

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)" || exit 1
CLASSIFIER="$SELF_DIR/classify-task.sh"
[ -x "$CLASSIFIER" ] || { printf 'Missing executable classifier: %s\n' "$CLASSIFIER" >&2; exit 1; }

CLASSIFICATION="$($CLASSIFIER --project "$PROJECT" --task "$TASK")" || exit 1

extract_scalar() {
  local key="$1"
  printf '%s\n' "$CLASSIFICATION" | sed -n "s/^  $key: '\(.*\)'$/\1/p" | sed "s/''/'/g" | head -1
}

extract_list() {
  local key="$1"
  printf '%s\n' "$CLASSIFICATION" | awk -v key="  $key:" '
    $0 == key { in_list = 1; next }
    in_list && /^  [a-z_]+:/ { in_list = 0 }
    in_list && /^    - / { print }
  ' | sed "s/^    - //; s/^'//; s/'$//; s/''/'/g" | sed '/^none$/d'
}

yaml_quote() {
  # Wrap in single quotes, escape embedded single quotes by doubling, and
  # collapse any CR/LF in the input to the literal characters \r/\n so the
  # emitted scalar stays a single YAML line. Newlines in user input would
  # otherwise break the output's structure (security review LOW-1).
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/''/g" | tr '\r' ' ' | awk 'BEGIN{ORS="\\n"} {print}' | sed 's/\\n$//')"
}

add_unique() {
  # First arg is an array name interpolated into an `eval` below. Defensive
  # validation: all current call sites pass a hardcoded uppercase identifier,
  # but the guard prevents shell-injection if a future refactor ever lets
  # user input reach here (security review INFO-2).
  local var_name="$1"
  case "$var_name" in
    ""|*[!A-Za-z0-9_]*|[0-9]*)
      printf 'add_unique: rejecting invalid variable name: %s\n' "$var_name" >&2
      return 2
      ;;
  esac
  local value="$2"
  [ -n "$value" ] || return 0
  eval "local existing=(\"\${${var_name}[@]}\")"
  local item
  for item in "${existing[@]}"; do
    [ "$item" = "$value" ] && return 0
  done
  eval "${var_name}+=(\"\$value\")"
}

print_list() {
  local var_name="$1"
  eval "local values=(\"\${${var_name}[@]}\")"
  if [ "${#values[@]}" -eq 0 ]; then
    printf '%s\n' "    - none"
    return
  fi
  local value
  for value in "${values[@]}"; do
    printf '    - %s\n' "$(yaml_quote "$value")"
  done
}

slug_role() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed 's# / #-#g; s# #\-#g'
}

skill_file() {
  case "$1" in
    python-pro) printf '%s\n' 'agent-team/skills/languages/python-pro.md' ;;
    typescript-pro) printf '%s\n' 'agent-team/skills/languages/typescript-pro.md' ;;
    javascript-pro) printf '%s\n' 'agent-team/skills/languages/javascript-pro.md' ;;
    sql-pro) printf '%s\n' 'agent-team/skills/languages/sql-pro.md' ;;
    java-pro) printf '%s\n' 'agent-team/skills/languages/java-pro.md' ;;
    csharp-pro) printf '%s\n' 'agent-team/skills/languages/csharp-pro.md' ;;
    cpp-pro) printf '%s\n' 'agent-team/skills/languages/cpp-pro.md' ;;
    go-pro) printf '%s\n' 'agent-team/skills/languages/go-pro.md' ;;
    rust-pro) printf '%s\n' 'agent-team/skills/languages/rust-pro.md' ;;
    php-pro) printf '%s\n' 'agent-team/skills/languages/php-pro.md' ;;
    shell-pro) printf '%s\n' 'agent-team/skills/languages/shell-pro.md' ;;
    fastapi) printf '%s\n' 'agent-team/skills/frameworks/fastapi.md' ;;
    react) printf '%s\n' 'agent-team/skills/frontend/react.md' ;;
    kubernetes) printf '%s\n' 'agent-team/skills/platform/kubernetes.md' ;;
    reviewer-pro) printf '%s\n' 'agent-team/skills/professional/reviewer-pro.md' ;;
    product-owner-pro) printf '%s\n' 'agent-team/skills/professional/product-owner-pro.md' ;;
    software-architecture) printf '%s\n' 'agent-team/skills/professional/software-architecture.md' ;;
    llm-pro) printf '%s\n' 'agent-team/skills/professional/llm-pro.md' ;;
    researcher-pro) printf '%s\n' 'agent-team/skills/professional/researcher-pro.md' ;;
    cnn) printf '%s\n' 'agent-team/skills/ml/cnn.md' ;;
  esac
}

LANE="$(extract_scalar lane)"
RISK="$(extract_scalar risk)"
INTENT="$(extract_scalar intent)"
PROFILE="$(extract_scalar quality_profile)"
RECIPE="$(extract_scalar recipe)"
STARTING_ROLE="$(extract_scalar starting_role)"

mapfile -t SKILLS < <(extract_list skills)
mapfile -t REVIEWERS < <(extract_list reviewers)
mapfile -t SPECIALISTS < <(extract_list specialists)
mapfile -t GATES < <(extract_list gates)

LOAD_NOW=()
LOAD_LATER=()
NOTES=()

if [ "$INTENT" = "direct_answer_or_advisory" ]; then
  printf '%s\n' 'context_manifest:'
  printf '  task: %s\n' "$(yaml_quote "$TASK")"
  printf '%s\n' "  lane: 'Direct Answer Mode'"
  printf '%s\n' "  risk: 'low'"
  printf '%s\n' "  quality_profile: 'light'"
  printf '%s\n' "  recipe: 'advisory'"
  printf '%s\n' "  starting_role: 'None'"
  printf '%s\n' '  load_now:'
  printf '%s\n' "    - 'none'"
  printf '%s\n' '  load_later:'
  printf '%s\n' "    - 'none unless the user asks for implementation, review, validation, or evidence'"
  printf '%s\n' '  notes:'
  printf '%s\n' "    - 'Answer directly from available context.'"
  printf '%s\n' "    - 'Do not create .agent-state artifacts.'"
  printf '%s\n' "    - 'Do not load roles, Skills, templates, docs, examples, or playbooks.'"
  exit 0
fi

add_unique LOAD_NOW 'agent-team/context/route-index.md'
add_unique LOAD_NOW 'agent-team/protocols/token-discipline.md'

case "$INTENT" in
  code_or_pr_review)
    add_unique LOAD_NOW 'agent-team/context/review-context.md'
    ;;
  source_backed_research_or_current_info)
    add_unique LOAD_NOW 'agent-team/context/research-context.md'
    ;;
  *)
    case "$LANE" in
      Fast*) add_unique LOAD_NOW 'agent-team/context/fast-lane-context.md' ;;
      *) add_unique LOAD_NOW 'agent-team/context/full-lane-context.md' ;;
    esac
    ;;
esac

if [ -n "$STARTING_ROLE" ]; then
  add_unique LOAD_NOW "agent-team/agents/$(slug_role "$STARTING_ROLE").md"
fi

add_unique LOAD_NOW 'agent-team/skills/registry.md'
for skill in "${SKILLS[@]}"; do
  file="$(skill_file "$skill")"
  [ -n "$file" ] && add_unique LOAD_NOW "$file"
done

[ -n "$RECIPE" ] && [ "$RECIPE" != "bug-fix" ] && add_unique LOAD_NOW "agent-team/recipes/$RECIPE.md"
if [ "$RECIPE" = "portfolio-project" ]; then
  add_unique LOAD_NOW 'agent-team/playbooks/portfolio-project-scope.md'
  add_unique LOAD_NOW 'agent-team/templates/role-fit-matrix.md'
  add_unique LOAD_NOW 'agent-team/templates/mvp-scope.md'
  add_unique LOAD_LATER 'agent-team/templates/resume-bullets.md'
  add_unique LOAD_LATER 'agent-team/templates/demo-script.md'
fi
if [ "$PROFILE" != "standard" ] || [ "${LANE#Fast}" = "$LANE" ]; then
  add_unique LOAD_NOW 'agent-team/playbooks/quality-profile-selection.md'
  [ -n "$PROFILE" ] && add_unique LOAD_NOW "agent-team/quality-profiles/$PROFILE.md"
fi

case "$LANE" in
  Fast*)
    add_unique LOAD_LATER 'agent-team/agents/tester.md'
    add_unique LOAD_LATER 'agent-team/templates/compact-test-report.md'
    add_unique LOAD_LATER 'agent-team/templates/compact-handoff.md'
    ;;
  *)
    add_unique LOAD_LATER 'agent-team/playbooks/full-lane.md'
    add_unique LOAD_LATER 'agent-team/playbooks/task-classification.md'
    add_unique LOAD_LATER 'agent-team/playbooks/lane-escalation.md'
    for role in 'Product Manager' 'Developer' 'Tester' 'Reviewer'; do
      [ "$role" = "$STARTING_ROLE" ] || add_unique LOAD_LATER "agent-team/agents/$(slug_role "$role").md"
    done
    ;;
esac

for reviewer in "${REVIEWERS[@]}"; do
  case "$reviewer" in
    Reviewer) add_unique LOAD_LATER 'agent-team/agents/reviewer.md'; add_unique LOAD_LATER 'agent-team/templates/compact-review-report.md' ;;
    'Product Manager') add_unique LOAD_LATER 'agent-team/agents/product-manager.md'; add_unique LOAD_LATER 'agent-team/templates/task.md' ;;
  esac
done

if [ "${#SPECIALISTS[@]}" -gt 0 ]; then
  add_unique LOAD_LATER 'agent-team/playbooks/specialist-review-routing.md'
fi
for specialist in "${SPECIALISTS[@]}"; do
  case "$specialist" in
    'Software Architect Agent')
      [ "$STARTING_ROLE" = 'Software Architect Agent' ] || add_unique LOAD_LATER 'agent-team/agents/software-architect-agent.md'
      add_unique LOAD_LATER 'agent-team/templates/architecture-report.md'
      ;;
    'Security Reviewer') add_unique LOAD_LATER 'agent-team/agents/security-reviewer.md'; add_unique LOAD_LATER 'agent-team/templates/security-review-report.md' ;;
    'UX / Design Reviewer') add_unique LOAD_LATER 'agent-team/agents/ux-design-reviewer.md'; add_unique LOAD_LATER 'agent-team/templates/ux-design-review-report.md' ;;
    'Documentation Agent') add_unique LOAD_LATER 'agent-team/agents/documentation-agent.md'; add_unique LOAD_LATER 'agent-team/templates/documentation-report.md' ;;
    'Support Triage Agent') add_unique LOAD_LATER 'agent-team/agents/support-triage-agent.md'; add_unique LOAD_LATER 'agent-team/templates/support-triage-report.md' ;;
    'Release Manager') add_unique LOAD_LATER 'agent-team/agents/release-manager.md'; add_unique LOAD_LATER 'agent-team/templates/release-report.md' ;;
    'LLM Agent') add_unique LOAD_LATER 'agent-team/agents/llm-agent.md'; add_unique LOAD_LATER 'agent-team/templates/llm-report.md' ;;
    'Researcher Agent') add_unique LOAD_LATER 'agent-team/agents/researcher-agent.md'; add_unique LOAD_LATER 'agent-team/templates/compact-research-report.md' ;;
    'CNN Agent') add_unique LOAD_LATER 'agent-team/agents/cnn-agent.md'; add_unique LOAD_LATER 'agent-team/templates/cnn-report.md' ;;
    'Skill Validator') add_unique LOAD_LATER 'agent-team/agents/skill-validator.md'; add_unique LOAD_LATER 'agent-team/templates/skill-validation-report.md' ;;
  esac
done

for gate in "${GATES[@]}"; do
  case "$gate" in
    *architecture*) add_unique LOAD_LATER 'agent-team/playbooks/architecture-decisions.md'; add_unique LOAD_LATER 'agent-team/checklists/architecture-review.md'; add_unique LOAD_LATER 'agent-team/templates/architecture-report.md' ;;
    *supply-chain*) add_unique LOAD_LATER 'agent-team/playbooks/dependency-supply-chain.md' ;;
    *refactor*) add_unique LOAD_LATER 'agent-team/playbooks/behavior-preserving-refactor.md' ;;
    *compatibility*) add_unique LOAD_LATER 'agent-team/playbooks/compatibility-rollout.md' ;;
    *integration*) add_unique LOAD_LATER 'agent-team/checklists/integration-test-escalation.md' ;;
    *portfolio*) add_unique LOAD_LATER 'agent-team/playbooks/portfolio-project-scope.md' ;;
    *target-role*) add_unique LOAD_LATER 'agent-team/playbooks/portfolio-project-scope.md' ;;
    *cloud*) add_unique LOAD_LATER 'agent-team/playbooks/cloud-operations.md'; add_unique LOAD_LATER 'agent-team/checklists/cloud-operation.md'; add_unique LOAD_LATER 'agent-team/templates/cloud-resources.md' ;;
    *artifact*) add_unique LOAD_LATER 'agent-team/playbooks/artifact-classification.md'; add_unique LOAD_LATER 'agent-team/templates/artifact-map.md' ;;
    *public/private*) add_unique LOAD_LATER 'agent-team/playbooks/public-private-boundary.md'; add_unique LOAD_LATER 'agent-team/playbooks/artifact-classification.md' ;;
    *constraints*) add_unique LOAD_LATER 'agent-team/playbooks/project-constraints.md'; add_unique LOAD_LATER 'agent-team/templates/project-constraints.md' ;;
    *no-commit*) add_unique LOAD_LATER 'agent-team/playbooks/project-constraints.md'; add_unique LOAD_LATER 'agent-team/checklists/project-constraints.md' ;;
  esac
done

add_unique NOTES 'Load now is the minimum context for the next phase.'
add_unique NOTES 'Load later only when that phase or gate is reached.'
add_unique NOTES 'Do not load docs, examples, STRUCTURE, or all Skills during target-project work.'

printf '%s\n' 'context_manifest:'
printf '  task: %s\n' "$(yaml_quote "$TASK")"
printf '  lane: %s\n' "$(yaml_quote "$LANE")"
printf '  risk: %s\n' "$(yaml_quote "$RISK")"
printf '  quality_profile: %s\n' "$(yaml_quote "$PROFILE")"
printf '  recipe: %s\n' "$(yaml_quote "$RECIPE")"
printf '  starting_role: %s\n' "$(yaml_quote "$STARTING_ROLE")"
printf '%s\n' '  load_now:'
print_list LOAD_NOW
printf '%s\n' '  load_later:'
print_list LOAD_LATER
printf '%s\n' '  notes:'
print_list NOTES
