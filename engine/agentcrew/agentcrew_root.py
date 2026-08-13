"""Locate the AgentCrew root that the engine executes against.

The methodology (agent-team/) lives in the same repo as the engine.
This module is the single place that resolves where the AgentCrew root is —
the engine reads role markdown, playbooks, templates, the classifier script,
and the protocols at runtime.

Search order:
  1. Explicit `root` argument (CLI flag --agentcrew-root)
  2. `AGENTCREW_ROOT` environment variable
  3. Sibling check: ./../ (engine/ sits under the AgentCrew root)
  4. `~/AgentCrew` if it looks like an install
  5. Error with actionable message

Resolution requires the candidate to actually look like AgentCrew:
  - AGENTS.md exists
  - agent-team/ exists
  - bin/agentcrew exists and is executable
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


_REQUIRED_FILES = (
    "AGENTS.md",
    "agent-team",
    "agent-team/agents",
    "agent-team/templates",
    "agent-team/playbooks",
    "agent-team/protocols",
    "agent-team/tools/classify-task.sh",
    "bin/agentcrew",
)


def _looks_like_install(path: Path) -> bool:
    if not path.is_dir():
        return False
    for req in _REQUIRED_FILES:
        if not (path / req).exists():
            return False
    return True


@dataclass(frozen=True)
class AgentCrewRoot:
    """A validated AgentCrew installation root."""

    path: Path

    def role_file(self, role: str) -> Path:
        """Map a role name (e.g. 'UX / Design Reviewer') to its markdown file."""
        slug = _role_slug(role)
        candidate = self.path / "agent-team" / "agents" / f"{slug}.md"
        if not candidate.exists():
            raise FileNotFoundError(
                f"Role {role!r} -> {candidate} not found. "
                f"Check AVAILABLE_ROLES against agent-team/agents/."
            )
        return candidate

    def methodology_file(self, relpath: str) -> Path:
        """Read any file under agent-team/ (e.g. recipes/bug-fix.md, quality-profiles/strict.md)."""
        if relpath.startswith("/") or ".." in relpath.split("/"):
            raise ValueError(f"relpath must be relative and not escape: {relpath!r}")
        candidate = self.path / relpath
        if not candidate.exists():
            raise FileNotFoundError(f"methodology file not found: {candidate}")
        return candidate

    @property
    def classifier(self) -> Path:
        return self.path / "agent-team" / "tools" / "classify-task.sh"

    @property
    def agentcrew_bin(self) -> Path:
        return self.path / "bin" / "agentcrew"


def _role_slug(role: str) -> str:
    """Map role names to their file slugs.

    Slug rule: lowercase, ' / ' -> '-', ' ' -> '-'.
    Examples:
      'Developer'              -> 'developer'
      'Security Reviewer'      -> 'security-reviewer'
      'UX / Design Reviewer'   -> 'ux-design-reviewer'
      'Documentation Agent'    -> 'documentation-agent'
      'Support Triage Agent'   -> 'support-triage-agent'
      'Software Architect Agent' -> 'software-architect-agent'
    """
    return role.lower().replace(" / ", "-").replace(" ", "-")


def find_agentcrew_root(explicit: Path | str | None = None) -> AgentCrewRoot:
    """Resolve the AgentCrew root. Raises FileNotFoundError if nothing valid.

    Honors `explicit` as a hard constraint: if you passed --agentcrew-root,
    we use that path or fail — we do NOT silently fall back to a sibling
    install. That would mask configuration mistakes (e.g. typo in the path)
    and run against a different AgentCrew than the user expected.
    """
    if explicit:
        candidate = Path(explicit).resolve()
        if _looks_like_install(candidate):
            return AgentCrewRoot(path=candidate)
        raise FileNotFoundError(
            f"--agentcrew-root {candidate} does not look like an AgentCrew install. "
            f"Missing one of: {', '.join(_REQUIRED_FILES)}"
        )

    candidates: list[tuple[str, Path]] = []
    env = os.environ.get("AGENTCREW_ROOT")
    if env:
        candidates.append(("AGENTCREW_ROOT", Path(env)))
    candidates.append(("sibling (../)", Path(__file__).resolve().parent.parent.parent))
    candidates.append(("~/AgentCrew", Path.home() / "AgentCrew"))

    for label, candidate in candidates:
        if _looks_like_install(candidate.resolve()):
            return AgentCrewRoot(path=candidate.resolve())

    tried = "\n".join(f"  - {label}: {p.resolve()}" for label, p in candidates)
    raise FileNotFoundError(
        "Could not locate an AgentCrew installation. Tried:\n"
        f"{tried}\n\n"
        "Pass --agentcrew-root /path/to/AgentCrew or set AGENTCREW_ROOT."
    )


# Role names (mirror of agent-team/agents/*.md).
# Order matters where the classifier emits a workflow string and we walk it.
AVAILABLE_ROLES: tuple[str, ...] = (
    "Advisor",
    "Idea Consultant",
    "Product Manager",
    "Software Architect Agent",
    "Developer",
    "Tester",
    "Reviewer",
    "Security Reviewer",
    "UX / Design Reviewer",
    "Documentation Agent",
    "Support Triage Agent",
    "Release Manager",
    "Skill Validator",
    "LLM Agent",
    "Researcher Agent",
    "CNN Agent",
)
