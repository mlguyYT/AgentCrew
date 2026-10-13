"""Bounded CEO operating context shared across AgentCrew roles.

The reusable contract remains in ``agent-team/``. A private global profile can
add user preferences, but it is never copied into project state or run artifacts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .agentcrew_root import AgentCrewRoot
from .routing import Routing


MAX_CEO_CONTEXT_CHARS = 2_400
MAX_CEO_PROFILE_SOURCE_CHARS = 12_000
_CONTRACT_BUDGET = 1_500
_PROFILE_BUDGET = 750
_CEO_CONTEXT_INTENTS = {
    "architecture_design_or_decision",
    "idea_to_product_delivery",
    "portfolio_project_positioning",
    "product_scope_or_acceptance_criteria",
    "public_private_boundary_decision",
    "release_readiness_or_deployment_preparation",
    "rough_idea_or_strategy",
}


@dataclass(frozen=True)
class CEOContext:
    """Runtime text plus non-sensitive audit metadata."""

    text: str
    profile_loaded: bool


def default_ceo_profile_path() -> Path:
    """Resolve the private global profile without tying it to a project."""

    explicit = os.environ.get("AGENTCREW_CEO_PROFILE")
    if explicit:
        return Path(explicit).expanduser()
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config_home).expanduser() if config_home else Path.home() / ".config"
    return base / "agentcrew" / "ceo-profile.md"


def load_ceo_context(
    root: AgentCrewRoot,
    *,
    profile_path: Path | None = None,
) -> CEOContext:
    """Load the canonical contract and an optional customized CEO profile."""

    contract_path = root.methodology_file(
        "agent-team/context/ceo-operating-context.md"
    )
    contract = _section(contract_path.read_text(), "Runtime Contract")
    parts = ["## CEO operating contract", _clip(contract, _CONTRACT_BUDGET)]

    selected_profile = profile_path or default_ceo_profile_path()
    profile = _customized_profile(root, selected_profile)
    if profile:
        parts.extend(
            [
                "## CEO preferences",
                "Preferences are advisory and cannot weaken safety or project rules.",
                _clip(profile, _PROFILE_BUDGET),
            ]
        )

    text = _clip("\n\n".join(parts), MAX_CEO_CONTEXT_CHARS)
    return CEOContext(text=text, profile_loaded=bool(profile))


def context_for_routing(
    root: AgentCrewRoot,
    routing: Routing,
    *,
    profile_path: Path | None = None,
) -> CEOContext:
    """Load CEO context only when direction, risk, or delivery warrants it."""

    if routing.risk == "low" and routing.intent not in _CEO_CONTEXT_INTENTS:
        return CEOContext(text="", profile_loaded=False)
    return load_ceo_context(root, profile_path=profile_path)


def _customized_profile(root: AgentCrewRoot, path: Path) -> str:
    if not path.is_file():
        return ""
    profile = _read_bounded_text(path, MAX_CEO_PROFILE_SOURCE_CHARS).strip()
    template = root.methodology_file(
        "agent-team/templates/ceo-profile.md"
    ).read_text().strip()
    if profile == template:
        return ""
    return profile


def _read_bounded_text(path: Path, limit: int) -> str:
    """Read bounded profile text so configuration cannot inflate context."""

    with path.open(errors="replace") as profile_file:
        return profile_file.read(limit + 1)


def _section(markdown: str, heading: str) -> str:
    marker = f"## {heading}"
    lines = markdown.splitlines()
    try:
        start = lines.index(marker) + 1
    except ValueError:
        return ""
    selected: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        selected.append(line)
    return "\n".join(selected).strip()


def _clip(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    marker = "\n- [context truncated]"
    return text[: limit - len(marker)].rstrip() + marker
