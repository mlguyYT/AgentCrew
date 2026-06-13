"""Gate playbook loading — maps classifier gate names to playbook files.

When the classifier emits a gate like `dependency and supply-chain gate`,
the engine looks up the matching playbook in `agent-team/playbooks/` (or
`agent-team/checklists/`) and injects its full text into the relevant
role's context. The role agent gets to see the methodology's actual guidance,
verbatim, instead of just the gate name.

Mappings come from reading the classifier script: each gate string the
classifier can emit maps to a specific .md file in agent-team/.
"""

from __future__ import annotations

from pathlib import Path

from .agentcrew_root import AgentCrewRoot


# Gate string (lowercased) -> path under the AgentCrew root.
# Sources: agent-team/tools/classify-task.sh and protocols/state-artifacts.md.
_GATE_FILES: dict[str, str] = {
    "tester validation": "agent-team/checklists/testing.md",
    "validation report": "agent-team/checklists/testing.md",
    "review report": "agent-team/checklists/code-review.md",
    "documentation review": "agent-team/checklists/documentation.md",
    "support triage report": "agent-team/checklists/support-triage.md",
    "release report": "agent-team/checklists/release-readiness.md",
    "human release approval": "agent-team/checklists/human-approval.md",
    "source quality check": "agent-team/checklists/research-quality.md",
    "llm review": "agent-team/checklists/llm-review.md",
    "cnn review": "agent-team/checklists/cnn-review.md",
    "skill validation": "agent-team/checklists/skill-validation.md",
    "full validation": "agent-team/checklists/testing.md",
    "risk-based review": "agent-team/checklists/code-review.md",
    "specialist routing check": "agent-team/playbooks/specialist-review-routing.md",
    "specialist review when triggered": "agent-team/playbooks/specialist-review-routing.md",
    "product behavior review": "agent-team/checklists/acceptance-criteria.md",
    "portfolio scope check": "agent-team/playbooks/portfolio-project-scope.md",
    "target-role evidence check": "agent-team/playbooks/portfolio-project-scope.md",
    "dependency and supply-chain gate": "agent-team/playbooks/dependency-supply-chain.md",
    "behavior-preserving refactor check": "agent-team/playbooks/behavior-preserving-refactor.md",
    "compatibility rollout check": "agent-team/playbooks/compatibility-rollout.md",
    "integration-test need check": "agent-team/checklists/integration-test-escalation.md",
}


# Which roles should see which gates. A gate may be relevant to multiple
# roles (e.g. testing.md is for the Tester; dependency-supply-chain.md is
# for the Developer). Default: every role sees every triggered gate.
# This map narrows: only the listed roles get the gate injected into
# their context. Empty means "all roles".
_GATE_ROLES: dict[str, set[str]] = {
    "tester validation": {"Tester"},
    "validation report": {"Tester"},
    "full validation": {"Tester"},
    "review report": {"Reviewer"},
    "risk-based review": {"Reviewer"},
    "documentation review": {"Documentation Agent"},
    "support triage report": {"Support Triage Agent"},
    "release report": {"Release Manager"},
    "human release approval": {"Release Manager"},
    "source quality check": {"Researcher Agent"},
    "llm review": {"LLM Agent"},
    "cnn review": {"CNN Agent"},
    "skill validation": {"Skill Validator"},
    "dependency and supply-chain gate": {"Developer", "Reviewer", "Security Reviewer"},
    "behavior-preserving refactor check": {"Developer", "Reviewer"},
    "compatibility rollout check": {"Developer", "Reviewer", "Security Reviewer"},
    "integration-test need check": {"Tester"},
    "product behavior review": {"Product Manager", "Reviewer"},
    "portfolio scope check": {"Product Manager", "Reviewer", "Documentation Agent"},
    "target-role evidence check": {"Product Manager", "Researcher Agent", "Documentation Agent"},
    "specialist routing check": set(),  # general, all roles
    "specialist review when triggered": set(),  # general, all roles
}


def load_gates_for_role(root: AgentCrewRoot, role: str, gates: list[str]) -> list[tuple[str, str]]:
    """Return [(gate_name, file_text)] for every gate that applies to this role.

    A gate applies when:
      - it has a known mapping in _GATE_FILES, AND
      - the role is in its _GATE_ROLES allowlist (or the allowlist is empty
        which means 'all roles').

    Silently skips unknown gates and missing playbook files so a methodology file
    rename doesn't break the engine. Returns an empty list when nothing
    applies — the orchestrator omits the section entirely in that case.
    """
    out: list[tuple[str, str]] = []
    for gate in gates:
        key = gate.strip().lower()
        relpath = _GATE_FILES.get(key)
        if not relpath:
            continue
        relevant_roles = _GATE_ROLES.get(key, set())
        if relevant_roles and role not in relevant_roles:
            continue
        try:
            text = root.methodology_file(relpath).read_text()
        except FileNotFoundError:
            continue
        out.append((gate, text))
    return out


def render_gate_section(gate_texts: list[tuple[str, str]]) -> str:
    """Render gate playbooks as a context block for the role's user message."""
    if not gate_texts:
        return ""
    parts = [
        "## Triggered gates for your role",
        "",
        "the classifier flagged these gates for this task. Apply the guidance "
        "below as part of your work.",
        "",
    ]
    for gate, text in gate_texts:
        parts.append(f"### Gate: `{gate}`")
        parts.append("")
        parts.append(text.strip())
        parts.append("")
    return "\n".join(parts)
