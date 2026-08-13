"""First-class local backend — runs everything on your machine.

This is just a thin layer on top of the OpenAI-compatible HTTP adapter,
but with defaults tuned for local inference:
  - base_url defaults to http://localhost:11434/v1  (Ollama)
  - no API key required
  - on construction, probes /api/tags so you fail fast with a useful
    message if Ollama (or your local server) isn't running
  - exposes `recommended_models_for_code()` so users can get a working
    setup without having to know the names

Compatibility: any local server that implements OpenAI Chat Completions
with tool calling works. As of writing that includes:

  - **Ollama 0.5+** (default for this provider)
  - **vLLM** (with `--enable-auto-tool-choice` and a tool-capable model)
  - **LM Studio** (1.4+, when the loaded model supports tools)
  - **llama.cpp server** (when running with `--jinja --chat-template-file`
    for a tool-capable template)
  - **MLX-LM** via the openai-compatible wrapper

If you're on a different local stack and tool calling isn't working,
drop a sibling provider_<name>.py that talks to your stack natively.
"""

from __future__ import annotations

import os

from .provider_openai import OpenAICompatibleProvider


_OLLAMA_DEFAULT = "http://localhost:11434"


def recommended_models_for_code() -> dict[str, list[str]]:
    """Per-role suggestions, ordered by quality-then-size.

    These are starting points, not guarantees. Tool-call quality on local
    models has improved a lot in 2024-2026 but still varies by model and
    quantization. Use `ollama pull <name>` to fetch.
    """
    return {
        "Product Manager": [
            "qwen2.5-coder:32b",
            "qwen2.5:32b",
            "llama3.3:70b",
            "qwen2.5-coder:14b",
        ],
        "Developer": [
            "qwen2.5-coder:32b",
            "deepseek-coder-v2:16b",
            "qwen2.5-coder:14b",
            "qwen2.5-coder:7b",
        ],
        "Tester": [
            "qwen2.5-coder:14b",
            "qwen2.5-coder:7b",
            "qwen2.5:14b",
        ],
        "Reviewer": [
            "qwen2.5-coder:32b",
            "llama3.3:70b",
            "qwen2.5:32b",
        ],
        "Software Architect Agent": [
            "qwen2.5-coder:32b",
            "llama3.3:70b",
            "qwen2.5:32b",
        ],
        "Researcher Agent": [
            "qwen2.5:14b",
            "llama3.1:8b",
        ],
        "Security Reviewer": [
            "qwen2.5-coder:32b",
            "llama3.3:70b",
        ],
        "Documentation Agent": [
            "qwen2.5:14b",
            "llama3.1:8b",
            "qwen2.5:7b",
        ],
    }


class LocalProvider(OpenAICompatibleProvider):
    """Local inference backend (Ollama-first).

    Construct it with a base URL pointing at any OpenAI-compatible local
    server. The default expects Ollama at its default port. Pass
    `probe=False` to skip the startup health check.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 300.0,
        probe: bool = True,
    ) -> None:
        # Ollama's OpenAI-compatible endpoint is at /v1.
        resolved_base = (
            base_url
            or os.environ.get("AGENTCREW_LOCAL_BASE_URL")
            or f"{_OLLAMA_DEFAULT}/v1"
        )
        # Ollama doesn't require a token, but downstream code expects a string.
        super().__init__(
            base_url=resolved_base,
            api_key=api_key or os.environ.get("AGENTCREW_LOCAL_API_KEY") or "local",
            timeout=timeout,
        )
        if probe:
            self._probe()

    def _probe(self) -> None:
        """Best-effort check that the local server is alive. Don't fail
        construction if probing isn't possible; just print a hint."""
        import httpx

        # The Ollama-native /api/tags endpoint is the cheapest "are you up?"
        # check that also returns the list of pulled models.
        root = self._base_url.rsplit("/v1", 1)[0]
        candidates = [
            f"{root}/api/tags",          # Ollama native
            f"{self._base_url}/models",  # generic OpenAI-compatible
        ]
        last_err: Exception | None = None
        for url in candidates:
            try:
                with httpx.Client(timeout=3.0) as client:
                    r = client.get(url)
                    if r.status_code == 200:
                        return
                    last_err = RuntimeError(f"{url} → HTTP {r.status_code}")
            except Exception as exc:  # noqa: BLE001
                last_err = exc
        raise RuntimeError(
            f"Could not reach a local LLM server at {self._base_url}. "
            f"If you're using Ollama, run `ollama serve` and then "
            f"`ollama pull qwen2.5-coder:7b` (or any tool-capable model). "
            f"Last error: {last_err}"
        )

    def list_local_models(self) -> list[str]:
        """Return the list of model names currently available locally.

        Tries Ollama's `/api/tags` first, then falls back to the
        OpenAI-compatible `/v1/models` shape. Empty list on failure.
        """
        import httpx

        root = self._base_url.rsplit("/v1", 1)[0]
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(f"{root}/api/tags")
                if r.status_code == 200:
                    return [m["name"] for m in r.json().get("models", [])]
                r = client.get(f"{self._base_url}/models")
                if r.status_code == 200:
                    return [m["id"] for m in r.json().get("data", [])]
        except Exception:  # noqa: BLE001
            return []
        return []
