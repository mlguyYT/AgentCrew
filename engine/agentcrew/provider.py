"""Provider — the only thing in core that knows about an LLM, and even it
doesn't know *which* LLM.

This module is intentionally vendor-free. It defines:
  - `Provider`  — the ABC every backend implements
  - `AgentRun`  — what `run_agent` returns
  - `MockProvider` — a deterministic test/demo backend with no network

Concrete backends live in sibling modules (`provider_anthropic.py`,
`provider_openai.py`, `provider_local.py`) and lazy-import their SDK so
the core install stays SDK-free.

The provider does not know the difference between Handoff and Plan — it
just exposes whatever submit-tool the orchestrator parameterizes and
returns the raw dict. The orchestrator parses it into a typed artifact.

Core depends on this file. This file depends on nothing platform-specific.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .tools import ToolError, ToolSpec


@dataclass
class AgentRun:
    """Result of one agent turn.

    `submission` is the raw dict the role passed to its submit-tool
    (`submit_handoff` for normal roles, `submit_plan` for the Planner).
    The orchestrator parses it into the right Pydantic type.

    Context metadata records which methodology fragments the orchestrator
    compiled for the run without storing another copy of their text.
    """

    submission: dict | None = None
    transcript: list[dict] = field(default_factory=list)
    tool_call_count: int = 0
    stop_reason: str = ""
    usage: dict = field(default_factory=dict)
    context_fragments: tuple[str, ...] = ()
    context_estimated_tokens: int = 0
    observed_changed_files: tuple[str, ...] = ()
    execution_evidence: dict = field(default_factory=dict)
    validation_evidence: dict = field(default_factory=dict)
    review_evidence: dict = field(default_factory=dict)


class Provider(ABC):
    """One turn: system prompt + user message + bounded tools → submitted dict.

    Implementations must:
      - call the relevant model with `system_prompt` as the system instruction
      - expose the listed tools, plus the parameterized submit_tool
      - execute tool calls locally by invoking `ToolSpec.handler`
      - stop after the model calls submit_tool_name (or after `max_iterations`)
      - return an `AgentRun` with the submitted input dict (or None on protocol failure)
    """

    @abstractmethod
    def run_agent(
        self,
        *,
        role: str,
        system_prompt: str,
        user_message: str,
        tools: list[ToolSpec],
        model: str,
        max_tokens: int,
        max_iterations: int,
        submit_tool_name: str,
        submit_tool_description: str,
        submit_tool_schema: dict,
    ) -> AgentRun:
        ...


@dataclass
class ScriptedTurn:
    """One turn of a scripted mock: zero or more tool calls, then a submission."""

    tool_calls: list[dict] = field(default_factory=list)  # [{"name", "input"}]
    submission: dict | None = None
    submission_tool: str | None = None  # defaults to whatever the role's submit tool is


class MockProvider(Provider):
    """Replays a per-role script of turns. Tool calls execute locally — only
    the model's responses are mocked. This is the test/demo backend; it has
    zero LLM dependency, runs offline, and is fully deterministic."""

    def __init__(self, scripts: dict[str, list[ScriptedTurn]]) -> None:
        self._scripts = {role: list(turns) for role, turns in scripts.items()}

    def run_agent(
        self,
        *,
        role: str,
        system_prompt: str,
        user_message: str,
        tools: list[ToolSpec],
        model: str,
        max_tokens: int,
        max_iterations: int,
        submit_tool_name: str,
        submit_tool_description: str,
        submit_tool_schema: dict,
    ) -> AgentRun:
        run = AgentRun()
        tool_by_name = {t.name: t for t in tools}
        script = self._scripts.get(role, [])
        if not script:
            raise RuntimeError(f"MockProvider has no script for role {role!r}")

        turn = script.pop(0)
        for call in turn.tool_calls:
            run.tool_call_count += 1
            name = call["name"]
            tinput = call["input"]
            if name not in tool_by_name:
                run.transcript.append(
                    {"role": "tool", "name": name, "result": "denied (not in allowlist)", "is_error": True}
                )
                continue
            try:
                result = tool_by_name[name].handler(**tinput)
                run.transcript.append({"role": "tool", "name": name, "result": result[:1000]})
            except ToolError as exc:
                run.transcript.append(
                    {"role": "tool", "name": name, "result": str(exc), "is_error": True}
                )

        if turn.submission is not None:
            run.submission = turn.submission
            run.stop_reason = submit_tool_name

        return run


def load_provider(name: str, **kwargs) -> Provider:
    """Lazy-load a provider by short name. Lets the CLI accept --backend X
    without forcing all SDK extras to be installed."""
    if name == "mock":
        return MockProvider(scripts=kwargs.get("scripts", {}))
    if name == "anthropic":
        from .provider_anthropic import AnthropicProvider

        return AnthropicProvider(**kwargs)
    if name == "openai":
        from .provider_openai import OpenAICompatibleProvider

        return OpenAICompatibleProvider(**kwargs)
    if name == "local":
        from .provider_local import LocalProvider

        return LocalProvider(**kwargs)
    raise ValueError(
        f"Unknown backend {name!r}. Built-in options: anthropic, openai, local, mock. "
        f"To add another, drop a provider_<name>.py module and extend load_provider()."
    )
