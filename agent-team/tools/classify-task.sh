#!/usr/bin/env bash
set -u

usage() {
  printf '%s\n' "Usage: classify-task.sh --task TEXT [options]"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --task TEXT         User request to classify"
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

if [ ! -d "$PROJECT" ]; then
  printf 'Project path does not exist: %s\n' "$PROJECT" >&2
  exit 1
fi

PROJECT_ABS="$(cd "$PROJECT" && pwd -P)" || exit 1
PROJECT_ROOT="$PROJECT_ABS"
if git -C "$PROJECT_ABS" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_ROOT="$(git -C "$PROJECT_ABS" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PROJECT_ABS")"
fi

TASK_LOWER="$(printf '%s' "$TASK" | tr '[:upper:]' '[:lower:]')"

matches() {
  printf '%s\n' "$TASK_LOWER" | grep -Eiq "$1"
}

add_unique() {
  local var_name="$1"
  local value="$2"
  eval "local existing=(\"\${${var_name}[@]}\")"
  local item
  for item in "${existing[@]}"; do
    [ "$item" = "$value" ] && return 0
  done
  eval "${var_name}+=(\"\$value\")"
}

yaml_quote() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/''/g")"
}

print_yaml_list() {
  local var_name="$1"
  eval "local values=(\"\${${var_name}[@]}\")"
  if [ "${#values[@]}" -eq 0 ]; then
    printf '%s\n' "  - none"
    return
  fi
  local value
  for value in "${values[@]}"; do
    printf '  - %s\n' "$(yaml_quote "$value")"
  done
}

INTENT="implementation_or_bug_fix"
STARTING_ROLE="Developer"
RISK="low"
LANE="Fast Lane"
WORKFLOW="Developer -> Tester -> Human"
NEXT_ROLES=("Tester")
REVIEWERS=()
SPECIALISTS=()
SKILLS=()
GATES=()
HUMAN_DECISIONS=("final approval before merge")
REASONS=()
FILES_TO_LOAD=("agent-team/context/route-index.md" "agent-team/playbooks/request-routing.md" "agent-team/playbooks/task-classification.md")

# Intent mapping. Later rules may escalate risk without changing explicit intent.
if matches '(^| )(review|reviewer|code review|pr review|pull request review|audit)( |$)'; then
  INTENT="code_or_pr_review"
  STARTING_ROLE="Reviewer"
  WORKFLOW="Reviewer -> Human"
  NEXT_ROLES=("Human")
  add_unique SKILLS "reviewer-pro"
  add_unique REASONS "request asks for review or quality check"
elif matches '^(test|validate|verify|qa|run tests|run validation)|regression check'; then
  INTENT="validation_or_regression_check"
  STARTING_ROLE="Tester"
  WORKFLOW="Tester -> Human"
  NEXT_ROLES=("Human")
  add_unique REASONS "request asks for validation"
elif matches '(^| )(fix|change|add|update|create|build|implement|improve|refactor|remove|replace)( |$)'; then
  INTENT="implementation_or_bug_fix"
  STARTING_ROLE="Developer"
  WORKFLOW="Developer -> Tester -> Human"
  NEXT_ROLES=("Tester" "Human")
  add_unique REASONS "request asks for implementation"
elif matches '(research|compare|investigate options|source-backed|sources|citation|latest|current|market|standard|regulation)'; then
  INTENT="source_backed_research_or_current_info"
  STARTING_ROLE="Researcher Agent"
  WORKFLOW="Researcher Agent -> Product Manager if decision needed -> Human"
  NEXT_ROLES=("Product Manager if decision needed" "Human")
  add_unique SPECIALISTS "Researcher Agent"
  add_unique SKILLS "researcher-pro"
  add_unique REASONS "request needs research or external evidence"
elif matches '(docs|documentation|readme|changelog|release note|example|guide)'; then
  INTENT="docs_examples_or_changelog"
  STARTING_ROLE="Documentation Agent"
  WORKFLOW="Documentation Agent -> Tester/Reviewer if behavior claims changed -> Human"
  NEXT_ROLES=("Human")
  add_unique SPECIALISTS "Documentation Agent"
  add_unique REASONS "request targets documentation"
elif matches '(skill|skills registry|authoring guide)'; then
  INTENT="skill_creation_or_skill_change"
  STARTING_ROLE="Skill Validator"
  WORKFLOW="Skill Validator -> Human"
  NEXT_ROLES=("Human")
  add_unique SPECIALISTS "Skill Validator"
  add_unique REASONS "request changes or validates AgentCrew Skills"
elif matches '(llm|prompt|rag|embedding|vector search|tool calling|function calling|structured output|model selection|eval|hallucination|prompt injection)'; then
  INTENT="prompt_rag_tool_calling_or_model_behavior"
  STARTING_ROLE="LLM Agent"
  WORKFLOW="LLM Agent -> Developer/Tester if implementation follows -> Human"
  NEXT_ROLES=("Developer if implementation follows" "Tester" "Human")
  add_unique SPECIALISTS "LLM Agent"
  add_unique SKILLS "llm-pro"
  add_unique REASONS "request touches LLM behavior or safety"
elif matches '(cnn|computer vision|image classification|object detection|segmentation|image dataset|augmentation|model training|inference optimization)'; then
  INTENT="computer_vision_cnn_training_or_inference"
  STARTING_ROLE="CNN Agent"
  WORKFLOW="CNN Agent -> Developer/Tester if implementation follows -> Human"
  NEXT_ROLES=("Developer if implementation follows" "Tester" "Human")
  add_unique SPECIALISTS "CNN Agent"
  add_unique SKILLS "cnn"
  add_unique REASONS "request touches computer vision or CNN work"
elif matches '(idea|strategy|should we|evaluate|brainstorm|roadmap|positioning)'; then
  INTENT="rough_idea_or_strategy"
  STARTING_ROLE="Advisor"
  WORKFLOW="Advisor -> Idea Consultant -> Product Manager -> Human"
  NEXT_ROLES=("Idea Consultant" "Product Manager" "Human")
  add_unique REASONS "request needs idea or strategy evaluation"
elif matches '(plan|scope|requirements|acceptance criteria|backlog|user story|product behavior|feature)'; then
  INTENT="product_scope_or_acceptance_criteria"
  STARTING_ROLE="Product Manager"
  WORKFLOW="Product Manager -> Developer -> Tester -> Human"
  NEXT_ROLES=("Developer" "Tester" "Human")
  add_unique SKILLS "product-owner-pro"
  add_unique REASONS "request needs product scope or acceptance criteria"
fi

case "$INTENT" in
  implementation_or_bug_fix|product_scope_or_acceptance_criteria)
    add_unique GATES "tester validation"
    ;;
  validation_or_regression_check)
    add_unique GATES "validation report"
    ;;
  code_or_pr_review)
    add_unique GATES "review report"
    ;;
  docs_examples_or_changelog)
    add_unique GATES "documentation review"
    ;;
  source_backed_research_or_current_info)
    add_unique GATES "source quality check"
    ;;
  prompt_rag_tool_calling_or_model_behavior)
    add_unique GATES "LLM review"
    ;;
  computer_vision_cnn_training_or_inference)
    add_unique GATES "CNN review"
    ;;
  skill_creation_or_skill_change)
    add_unique GATES "Skill validation"
    ;;
esac

# Specialist triggers.
if matches '(auth|authentication|authorization|permission|permissions|secret|token|customer data|sensitive data|payment|billing|dependency|lockfile|runtime|container|docker|ci|build system|infrastructure|public api|input handling|injection)'; then
  add_unique SPECIALISTS "Security Reviewer"
  add_unique REASONS "security or supply-chain trigger present"
fi
if matches '(ui|ux|design|user-facing|onboarding|form|navigation|accessibility|responsive|layout|copy|visual)'; then
  add_unique SPECIALISTS "UX / Design Reviewer"
  add_unique REASONS "user-facing or design trigger present"
fi
if matches '(docs|documentation|readme|changelog|release note|example|guide|migration note|public api)'; then
  add_unique SPECIALISTS "Documentation Agent"
fi
if matches '(llm|prompt|rag|embedding|vector search|tool calling|function calling|structured output|model|eval|hallucination|prompt injection)'; then
  add_unique SPECIALISTS "LLM Agent"
  add_unique SKILLS "llm-pro"
fi
if matches '(research|compare|latest|current|market|standard|regulation|citation|source)'; then
  add_unique SPECIALISTS "Researcher Agent"
  add_unique SKILLS "researcher-pro"
fi
if matches '(cnn|computer vision|image classification|object detection|segmentation|image dataset|augmentation|training|inference)'; then
  add_unique SPECIALISTS "CNN Agent"
  add_unique SKILLS "cnn"
fi
if matches '(skill|skills registry|skill changed|new skill)'; then
  add_unique SPECIALISTS "Skill Validator"
fi

# Skill hints from task text.
if matches '(typescript|\.ts|\.tsx)'; then add_unique SKILLS "typescript-pro"; fi
if matches '(javascript|\.js|\.jsx|node|express|fastify|nestjs)'; then add_unique SKILLS "javascript-pro"; fi
if matches '(react|next\.js|nextjs|vite)'; then add_unique SKILLS "react"; fi
if matches '(python|pytest|django|flask|fastapi)'; then add_unique SKILLS "python-pro"; fi
if matches '(fastapi)'; then add_unique SKILLS "fastapi"; fi
if matches '(sql|database|migration|schema|query)'; then add_unique SKILLS "sql-pro"; fi
if matches '(java|spring|gradle|maven)'; then add_unique SKILLS "java-pro"; fi
if matches '(c#|\.net|dotnet)'; then add_unique SKILLS "csharp-pro"; fi
if matches '(c\+\+|cpp|cmake)'; then add_unique SKILLS "cpp-pro"; fi
if matches '(golang| go |go.mod)'; then add_unique SKILLS "go-pro"; fi
if matches '(rust|cargo)'; then add_unique SKILLS "rust-pro"; fi
if matches '(php|composer|laravel)'; then add_unique SKILLS "php-pro"; fi
if matches '(shell|bash|script|makefile)'; then add_unique SKILLS "shell-pro"; fi
if matches '(kubernetes|k8s|helm|deployment yaml|manifest)'; then add_unique SKILLS "kubernetes"; fi

# Risk classification. Critical overrides high, high overrides medium.
if matches '(delete data|data loss|drop table|destructive|force push|force-push|rewrite shared history|rotate production secret|changing payment flow|permission model|major architecture replacement)'; then
  RISK="critical"
  LANE="Full Lane plus explicit human decision"
  WORKFLOW="Advisor -> Idea Consultant -> Human decision -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer -> Human"
  add_unique HUMAN_DECISIONS "accept critical risk before implementation"
  add_unique REASONS "critical human-only decision trigger present"
elif matches '(auth|authentication|authorization|billing|payment|customer data|sensitive data|data write|migration|infrastructure|ci/cd|deployment|public api|protocol|compatibility|production config|default branch|large refactor|architecture|runtime|container|lockfile|dependency)'; then
  RISK="high"
  LANE="Full Lane"
  WORKFLOW="Advisor -> Idea Consultant -> Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human"
  add_unique REASONS "high-risk task classification trigger present"
elif matches '(new feature|api behavior|api change|database read|moderate refactor|user-facing|shared module|dependency update|runtime update|behavior change|scope change)'; then
  RISK="medium"
  LANE="Fast Lane with required review or Full Lane if unclear"
  WORKFLOW="Product Manager -> Developer -> Tester -> Reviewer -> Specialist Reviewer if needed -> Human"
  add_unique REASONS "medium-risk task classification trigger present"
else
  add_unique REASONS "small or scoped request with no high-risk trigger detected"
fi

# Role and gate adjustments after risk classification.
if [ "$RISK" = "high" ] || [ "$RISK" = "critical" ]; then
  if [ "$INTENT" = "implementation_or_bug_fix" ]; then
    STARTING_ROLE="Advisor"
    NEXT_ROLES=("Idea Consultant" "Product Manager" "Developer" "Tester" "Reviewer" "Human")
  fi
  add_unique REVIEWERS "Reviewer"
  add_unique GATES "full validation"
  add_unique GATES "specialist review when triggered"
elif [ "$RISK" = "medium" ]; then
  if [ "$INTENT" = "implementation_or_bug_fix" ]; then
    STARTING_ROLE="Product Manager"
    NEXT_ROLES=("Developer" "Tester" "Reviewer" "Human")
  fi
  add_unique REVIEWERS "Reviewer"
  add_unique GATES "risk-based review"
else
  if [ "$INTENT" = "implementation_or_bug_fix" ]; then
    NEXT_ROLES=("Tester" "Human")
  fi
fi

case "$INTENT" in
  source_backed_research_or_current_info)
    WORKFLOW="Researcher Agent -> Product Manager if decision needed -> Human"
    NEXT_ROLES=("Product Manager if decision needed" "Human")
    ;;
  code_or_pr_review)
    WORKFLOW="Reviewer -> Specialist Reviewer if needed -> Human"
    NEXT_ROLES=("Specialist Reviewer if needed" "Human")
    ;;
  validation_or_regression_check)
    WORKFLOW="Tester -> Reviewer if risk is meaningful -> Human"
    NEXT_ROLES=("Reviewer if risk is meaningful" "Human")
    ;;
  docs_examples_or_changelog)
    WORKFLOW="Documentation Agent -> Reviewer if behavior claims changed -> Human"
    NEXT_ROLES=("Reviewer if behavior claims changed" "Human")
    ;;
  prompt_rag_tool_calling_or_model_behavior)
    WORKFLOW="LLM Agent -> Developer/Tester if implementation follows -> Human"
    NEXT_ROLES=("Developer if implementation follows" "Tester if implementation follows" "Human")
    ;;
  computer_vision_cnn_training_or_inference)
    WORKFLOW="CNN Agent -> Developer/Tester if implementation follows -> Human"
    NEXT_ROLES=("Developer if implementation follows" "Tester if implementation follows" "Human")
    ;;
  skill_creation_or_skill_change)
    WORKFLOW="Skill Validator -> Human"
    NEXT_ROLES=("Human")
    ;;
esac

if matches '(user-facing|behavior|compatibility|rollout|migration|scope|acceptance criteria|unclear)'; then
  add_unique REVIEWERS "Product Manager"
  add_unique GATES "product behavior review"
fi
if [ "${#SPECIALISTS[@]}" -gt 0 ]; then
  add_unique GATES "specialist routing check"
fi
if matches '(dependency|lockfile|runtime|container|docker|ci|build system)'; then
  add_unique GATES "dependency and supply-chain gate"
fi
if matches '(refactor|modular|architecture|shared module)'; then
  add_unique GATES "behavior-preserving refactor check"
fi
if matches '(api|protocol|auth|config|client/server|compatibility|rollout)'; then
  add_unique GATES "compatibility rollout check"
fi
if matches '(database|cache|queue|socket|timer|filesystem|external service|distributed)'; then
  add_unique GATES "integration-test need check"
fi

# Files to load.
if [ "$LANE" = "Fast Lane" ]; then
  add_unique FILES_TO_LOAD "agent-team/context/fast-lane-context.md"
  add_unique FILES_TO_LOAD "agent-team/playbooks/fast-lane.md"
else
  add_unique FILES_TO_LOAD "agent-team/context/full-lane-context.md"
  add_unique FILES_TO_LOAD "agent-team/playbooks/full-lane.md"
fi
add_unique FILES_TO_LOAD "agent-team/agents/$(printf '%s' "$STARTING_ROLE" | tr '[:upper:]' '[:lower:]' | sed 's# / #-#g; s# #\-#g').md"
add_unique FILES_TO_LOAD "agent-team/skills/registry.md"
add_unique FILES_TO_LOAD "agent-team/templates/task-routing.md"
if [ "${#SPECIALISTS[@]}" -gt 0 ]; then
  add_unique FILES_TO_LOAD "agent-team/playbooks/specialist-review-routing.md"
fi

printf '%s\n' "task_classification:"
printf '  task: %s\n' "$(yaml_quote "$TASK")"
printf '  project: %s\n' "$(yaml_quote "$(basename "$PROJECT_ROOT")")"
printf '  intent: %s\n' "$(yaml_quote "$INTENT")"
printf '  risk: %s\n' "$(yaml_quote "$RISK")"
printf '  lane: %s\n' "$(yaml_quote "$LANE")"
printf '  starting_role: %s\n' "$(yaml_quote "$STARTING_ROLE")"
printf '  workflow: %s\n' "$(yaml_quote "$WORKFLOW")"
printf '%s\n' "  next_roles:"
print_yaml_list NEXT_ROLES
printf '%s\n' "  reviewers:"
print_yaml_list REVIEWERS
printf '%s\n' "  specialists:"
print_yaml_list SPECIALISTS
printf '%s\n' "  skills:"
print_yaml_list SKILLS
printf '%s\n' "  gates:"
print_yaml_list GATES
printf '%s\n' "  human_decisions:"
print_yaml_list HUMAN_DECISIONS
printf '%s\n' "  files_to_load:"
print_yaml_list FILES_TO_LOAD
printf '%s\n' "  reasons:"
print_yaml_list REASONS
printf '%s\n' "  note: 'Heuristic classification. Agents must still inspect repository context and apply AgentCrew safety rules.'"
