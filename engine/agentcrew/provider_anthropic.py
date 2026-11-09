"""Anthropic backend — one optional adapter, not the default.

Install with `pip install -e ".[anthropic]"`. The `anthropic` import below
fails loudly if you call this without installing the extra.

Like every provider, this is a translation layer between the AgentCrew core
(tools, handoff schema, run_agent contract) and one vendor's wire format.
Adding a new vendor means writing a new file like this one. The orchestrator,
roles, tools, and CLI never need to change.
"""

from __future__ import annotations

import os

from .provider import AgentRun, Provider
from .tools import ToolError, ToolSpec


class AnthropicProvider(Provider):
    """Anthropic Messages API backend.

    Defaults (overridable per call via Agent.model):
      - adaptive thinking with `effort=high`
      - prompt caching on the system prompt (role files are stable per task)
    """

    billing_provider = "anthropic"

    def __init__(self, api_key: str | None = None) -> None:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover — exercised only without extras
            raise ImportError(
                "AnthropicProvider requires the [anthropic] extra. "
                "Install with: pip install -e \".[anthropic]\""
            ) from exc
        self._anthropic = anthropic
        self._client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

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
        submit_tool = {
            "name": submit_tool_name,
            "description": submit_tool_description,
            "input_schema": submit_tool_schema,
        }
        api_tools = [
            {"name": t.name, "description": t.description, "input_schema": t.input_schema}
            for t in tools
        ] + [submit_tool]
        tool_by_name = {t.name: t for t in tools}

        system_blocks = [
            {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
        ]
        messages: list[dict] = [{"role": "user", "content": user_message}]

        run = AgentRun(model=model, provider="anthropic")

        for _ in range(max_iterations):
            try:
                response = self._client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_blocks,
                    tools=api_tools,
                    messages=messages,
                    thinking={"type": "adaptive"},
                    output_config={"effort": "high"},
                )
            except self._anthropic.APIError as exc:
                run.stop_reason = f"provider_error:{type(exc).__name__}"
                break

            usage = getattr(response, "usage", None)
            for key in (
                "input_tokens", "output_tokens",
                "cache_read_input_tokens", "cache_creation_input_tokens",
            ):
                run.usage[key] = run.usage.get(key, 0) + (getattr(usage, key, 0) or 0)
            run.stop_reason = response.stop_reason or ""
            messages.append({"role": "assistant", "content": response.content})

            for block in response.content:
                if block.type == "text":
                    run.transcript.append({"role": "assistant", "type": "text", "text": block.text})
                elif block.type == "tool_use":
                    run.transcript.append(
                        {"role": "assistant", "type": "tool_use", "name": block.name, "input": block.input, "id": block.id}
                    )

            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if not tool_uses:
                break

            tool_results = []
            for tu in tool_uses:
                run.tool_call_count += 1
                if tu.name == submit_tool_name:
                    if not isinstance(tu.input, dict):
                        run.submission = None
                        run.stop_reason = "protocol_error:invalid_submit_arguments"
                        return run
                    run.submission = dict(tu.input)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": tu.id, "content": "submission accepted"}
                    )
                elif tu.name in tool_by_name:
                    try:
                        result = tool_by_name[tu.name].handler(**tu.input)
                        is_error = False
                    except ToolError as exc:
                        result = str(exc)
                        is_error = True
                    except Exception as exc:  # noqa: BLE001
                        result = f"unexpected tool error: {exc}"
                        is_error = True
                    run.transcript.append({"role": "tool", "name": tu.name, "result": result[:1000], "is_error": is_error})
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": tu.id, "content": result, **({"is_error": True} if is_error else {})}
                    )
                else:
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": tu.id, "content": f"tool {tu.name!r} not in allowlist", "is_error": True}
                    )

            messages.append({"role": "user", "content": tool_results})
            if run.submission is not None:
                break

        return run
