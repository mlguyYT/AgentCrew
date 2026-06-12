"""Agents — role bindings backed by agent-team/agents/*.md.

the engine owns NO role markdown. Every role's system prompt is read at runtime
from the AgentCrew installation. The orchestrator builds an Agent by passing in
the role name + the resolved AgentCrewRoot + a model string; the role file
comes straight from disk.

Model selection is the caller's responsibility (CLI flags, env vars, or
a per-role config). the engine has no default model strings — AgentCrew is
platform-independent.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .agentcrew_root import AgentCrewRoot


@dataclass(frozen=True)
class Agent:
    """One role's runtime binding. The system prompt is the role file."""

    role: str               # e.g. 'Developer', 'Security Reviewer'
    role_file: Path         # Resolved by AgentCrewRoot.role_file()
    model: str              # Caller-chosen; passed to the provider verbatim
    max_tokens: int = 8192
    max_iterations: int = 12

    def system_prompt(self) -> str:
        return self.role_file.read_text()


def build_agent(root: AgentCrewRoot, role: str, model: str, *, max_tokens: int = 8192) -> Agent:
    """Resolve a role name to a runtime Agent."""
    return Agent(role=role, role_file=root.role_file(role), model=model, max_tokens=max_tokens)


def model_for_role(
    *,
    role: str,
    cli_models: dict[str, str],
    env_default: str | None,
) -> str | None:
    """Pick a model for this role.

    Priority: cli_models[role] -> AGENTCREW_<ROLE>_MODEL env var (caller-supplied
    via cli_models) -> env_default. Returns None if nothing matches; the
    caller decides whether to error or skip.
    """
    if role in cli_models and cli_models[role]:
        return cli_models[role]
    return env_default
