"""Compile bounded runtime guidance from the Markdown methodology.

The classifier selects recipes, Skills, and gates. This module turns only the
actionable sections of those files into a stable, provider-neutral context
capsule instead of injecting complete playbooks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .agentcrew_root import AgentCrewRoot
from .routing import Routing


MAX_EXECUTION_CONTEXT_CHARS = 4_800
_CORE_BUDGET = 1_900
_GATES_BUDGET = 1_100
_GATE_BUDGET = 550
_RECIPE_BUDGET = 650
_SKILLS_BUDGET = 750
_SKILL_BUDGET = 500
_SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_ROLE_CORE_PLAYBOOKS = {
    "Developer": (
        "developer-execution-loop",
        "Execution loop",
    ),
    "Tester": (
        "tester-validation-loop",
        "Validation loop",
    ),
    "Reviewer": (
        "reviewer-inspection-loop",
        "Inspection loop",
    ),
}


@dataclass(frozen=True)
class CompiledExecutionContext:
    """Bounded context and an audit-friendly list of included fragments."""

    text: str
    fragment_ids: tuple[str, ...]
    omitted_fragment_ids: tuple[str, ...]
    estimated_tokens: int


def _sections(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections.append(
                    (current_heading, "\n".join(current_lines).strip())
                )
            current_heading = line[3:].strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_lines).strip()))
    return sections


def _section(markdown: str, *headings: str) -> str:
    available = {heading.casefold(): body for heading, body in _sections(markdown)}
    for heading in headings:
        body = available.get(heading.casefold())
        if body:
            return body
    return ""


def _clip(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    marker = "\n- [runtime guidance truncated to context budget]"
    if limit <= len(marker):
        if limit <= 3:
            return "." * limit
        return text[: limit - 3].rstrip() + "..."
    prefix = text[: limit - len(marker)]
    if "\n" in prefix:
        prefix = prefix.rsplit("\n", 1)[0]
    return prefix.rstrip() + marker


def _actionable_gate_text(markdown: str) -> str:
    explicit = _section(markdown, "Runtime Contract")
    if explicit:
        return explicit

    selected: list[str] = []
    action_terms = (
        "required",
        "rules",
        "checklist",
        "recommended pattern",
        "before ",
        "during work",
        "after teardown",
        "human approval",
        "decision",
        "design",
        "evolution",
        "fitness",
    )
    for heading, body in _sections(markdown):
        normalized = heading.casefold()
        if any(term in normalized for term in action_terms) and body:
            selected.append(f"**{heading}:**\n{body}")
    if selected:
        return "\n\n".join(selected)
    return markdown.strip()


def _skill_file(root: AgentCrewRoot, skill: str) -> Path | None:
    if not _SAFE_SLUG.fullmatch(skill):
        return None
    matches = sorted(
        (root.path / "agent-team" / "skills").rglob(f"{skill}.md"),
        key=str,
    )
    return matches[0] if matches else None


def _skill_text(markdown: str, role: str) -> str:
    if role == "Developer":
        headings = ("Runtime Contract", "Developer instructions", "Instructions")
    elif role == "Tester":
        headings = ("Runtime Contract", "Testing guidance", "Instructions")
    else:
        headings = ("Runtime Contract", "Review checklist", "Instructions")
    return _section(markdown, *headings)


def _fragment(fragment_id: str, title: str, body: str) -> tuple[str, str]:
    return fragment_id, f"### {title}\n\n{body.strip()}"


def compile_execution_context(
    *,
    root: AgentCrewRoot,
    routing: Routing,
    role: str,
    gate_texts: list[tuple[str, str]],
) -> CompiledExecutionContext:
    """Compile selected methodology fragments under a hard character budget."""

    included: list[tuple[str, str]] = []
    omitted: list[str] = []

    core_playbook = _ROLE_CORE_PLAYBOOKS.get(role)
    if core_playbook:
        playbook_slug, title = core_playbook
        loop_path = root.methodology_file(
            f"agent-team/playbooks/{playbook_slug}.md"
        )
        loop_text = _section(loop_path.read_text(), "Runtime Contract")
        if loop_text:
            included.append(
                _fragment(
                    f"playbook:{playbook_slug}",
                    title,
                    _clip(loop_text, _CORE_BUDGET),
                )
            )

    gate_chars = 0
    per_gate_budget = min(
        _GATE_BUDGET,
        _GATES_BUDGET // max(len(gate_texts), 1),
    )
    for gate_name, markdown in gate_texts:
        fragment_id = f"gate:{gate_name}"
        body = _clip(_actionable_gate_text(markdown), per_gate_budget)
        if not body or gate_chars + len(body) > _GATES_BUDGET:
            omitted.append(fragment_id)
            continue
        included.append(_fragment(fragment_id, f"Gate: {gate_name}", body))
        gate_chars += len(body)

    if _SAFE_SLUG.fullmatch(routing.recipe):
        recipe_path = root.path / "agent-team" / "recipes" / f"{routing.recipe}.md"
        if recipe_path.is_file():
            recipe_text = _section(
                recipe_path.read_text(), "Runtime Contract", "Agent Focus"
            )
            if recipe_text:
                included.append(
                    _fragment(
                        f"recipe:{routing.recipe}",
                        f"Recipe: {routing.recipe}",
                        _clip(recipe_text, _RECIPE_BUDGET),
                    )
                )

    skill_chars = 0
    for skill in sorted(set(routing.skills)):
        fragment_id = f"skill:{skill}"
        path = _skill_file(root, skill)
        if path is None:
            omitted.append(fragment_id)
            continue
        body = _clip(_skill_text(path.read_text(), role), _SKILL_BUDGET)
        if not body or skill_chars + len(body) > _SKILLS_BUDGET:
            omitted.append(fragment_id)
            continue
        included.append(_fragment(fragment_id, f"Skill: {skill}", body))
        skill_chars += len(body)

    header = (
        "## AgentCrew runtime guidance\n\n"
        "Apply this bounded execution capsule with the target repository's "
        "instructions. Human approval and safety constraints remain final."
    )
    rendered = header
    rendered_ids: list[str] = []
    for fragment_id, block in included:
        candidate = f"{rendered}\n\n{block}"
        if len(candidate) > MAX_EXECUTION_CONTEXT_CHARS:
            omitted.append(fragment_id)
            continue
        rendered = candidate
        rendered_ids.append(fragment_id)

    if omitted:
        names = ", ".join(omitted)
        omission_note = (
            "\n\nAdditional selected fragments were omitted by the context "
            f"budget: {names}."
        )
        if len(rendered) + len(omission_note) <= MAX_EXECUTION_CONTEXT_CHARS:
            rendered += omission_note

    return CompiledExecutionContext(
        text=rendered,
        fragment_ids=tuple(rendered_ids),
        omitted_fragment_ids=tuple(omitted),
        estimated_tokens=(len(rendered) + 3) // 4,
    )
