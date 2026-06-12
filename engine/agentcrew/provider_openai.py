"""OpenAI-compatible HTTP backend — covers a large slice of the ecosystem
from one adapter:

  - OpenAI's own /v1/chat/completions
  - Local servers: Ollama, vLLM, llama.cpp, LM Studio, Text Generation WebUI
  - Aggregators / inference providers: Together, Groq, Anyscale, Fireworks,
    Mistral, DeepSeek, OpenRouter, …
  - Self-hosted compatible gateways

Configure via `base_url` (default OpenAI). The provider speaks plain HTTP
(no `openai` SDK) so users can point it anywhere that implements the
ChatCompletions tool-call surface. Install with: pip install -e ".[openai]"
(only `httpx` is needed).
"""

from __future__ import annotations

import json
import os

from .provider import AgentRun, Provider
from .tools import ToolError, ToolSpec


class OpenAICompatibleProvider(Provider):
    """Talks to any OpenAI Chat Completions endpoint with tool calling.

    Tested target: the published OpenAI Chat Completions spec. Servers that
    advertise compatibility (Ollama 0.5+, vLLM, Together, Groq, …) should
    work unmodified; if a particular server omits `tool_calls`, file a
    backend-specific provider rather than tweaking this one.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
        extra_headers: dict | None = None,
    ) -> None:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "OpenAICompatibleProvider requires the [openai] extra. "
                "Install with: pip install -e \".[openai]\""
            ) from exc
        self._httpx = httpx
        self._base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._timeout = timeout
        self._extra_headers = extra_headers or {}

    def _post(self, path: str, payload: dict) -> dict:
        headers = {"Content-Type": "application/json", **self._extra_headers}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        with self._httpx.Client(timeout=self._timeout) as client:
            response = client.post(f"{self._base_url}{path}", headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

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
        # OpenAI tool format wraps each tool in {"type": "function", "function": {...}}
        def _as_function(name: str, description: str, schema: dict) -> dict:
            return {"type": "function", "function": {"name": name, "description": description, "parameters": schema}}

        api_tools = [_as_function(t.name, t.description, t.input_schema) for t in tools]
        api_tools.append(
            _as_function(submit_tool_name, submit_tool_description, submit_tool_schema)
        )
        tool_by_name = {t.name: t for t in tools}

        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        run = AgentRun()

        for _ in range(max_iterations):
            payload = {
                "model": model,
                "messages": messages,
                "tools": api_tools,
                "max_tokens": max_tokens,
                "tool_choice": "auto",
            }
            data = self._post("/chat/completions", payload)
            choice = data["choices"][0]
            msg = choice["message"]
            run.stop_reason = choice.get("finish_reason", "")
            run.usage = data.get("usage", {})

            # Append the assistant turn to history *exactly* as the server sent it
            # so the next round-trip stays consistent with tool_call_ids.
            assistant_turn = {"role": "assistant"}
            if msg.get("content") is not None:
                assistant_turn["content"] = msg["content"]
                run.transcript.append({"role": "assistant", "type": "text", "text": msg["content"]})
            if msg.get("tool_calls"):
                assistant_turn["tool_calls"] = msg["tool_calls"]
            messages.append(assistant_turn)

            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                break

            for tc in tool_calls:
                run.tool_call_count += 1
                fn = tc.get("function") or {}
                name = fn.get("name", "")
                args_raw = fn.get("arguments") or "{}"
                try:
                    args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                except json.JSONDecodeError as exc:
                    messages.append(
                        {"role": "tool", "tool_call_id": tc["id"], "content": f"argument parse error: {exc}"}
                    )
                    continue

                if name == submit_tool_name:
                    run.submission = dict(args)
                    messages.append(
                        {"role": "tool", "tool_call_id": tc["id"], "content": "submission accepted"}
                    )
                elif name in tool_by_name:
                    try:
                        result_text = tool_by_name[name].handler(**args)
                    except ToolError as exc:
                        result_text = f"ERROR: {exc}"
                    except Exception as exc:  # noqa: BLE001
                        result_text = f"unexpected tool error: {exc}"
                    run.transcript.append({"role": "tool", "name": name, "result": result_text[:1000]})
                    messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result_text})
                else:
                    messages.append(
                        {"role": "tool", "tool_call_id": tc["id"], "content": f"tool {name!r} not in allowlist"}
                    )

            if run.submission is not None:
                break

        return run
