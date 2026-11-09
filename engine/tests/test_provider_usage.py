"""Offline provider accounting, including incomplete and failed agent runs."""

import json
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from agentcrew.cost import CostSummary, cost_summary
from agentcrew.provider import AgentRun, MockProvider, ScriptedTurn
from agentcrew.provider_anthropic import AnthropicProvider
from agentcrew.provider_openai import OpenAICompatibleProvider
from agentcrew.tools import ToolError, ToolSpec


class FakeAPIError(Exception):
    pass


@pytest.fixture(params=["openai", "anthropic"])
def backend(request):
    return request.param


@pytest.fixture
def provider_api(backend, monkeypatch):
    api = Mock()
    if backend == "openai":
        provider = OpenAICompatibleProvider(base_url="https://api.openai.com/v1", api_key="test-key")
        monkeypatch.setattr(provider, "_post", api)
    else:
        client = SimpleNamespace(messages=SimpleNamespace(create=api))
        monkeypatch.setitem(sys.modules, "anthropic", SimpleNamespace(
            Anthropic=Mock(return_value=client), APIError=FakeAPIError,
        ))
        provider = AnthropicProvider(api_key="test-key")
    return provider, api


def _response(backend, tool_name=None, usage=None):
    if backend == "openai":
        message = {"content": None, "tool_calls": []}
        if tool_name:
            message["tool_calls"].append({
                "id": "call-1", "type": "function",
                "function": {"name": tool_name, "arguments": json.dumps({})},
            })
        return {
            "choices": [{"message": message, "finish_reason": "tool_calls" if tool_name else "stop"}],
            "usage": usage,
        }
    content = []
    if tool_name:
        content.append(SimpleNamespace(type="tool_use", name=tool_name, input={}, id="call-1"))
    return SimpleNamespace(
        content=content, stop_reason="tool_use" if tool_name else "end_turn",
        usage=SimpleNamespace(**usage) if usage is not None else None,
    )


def _run(provider, **overrides):
    arguments = {
        "role": "Developer", "system_prompt": "system", "user_message": "task",
        "tools": [ToolSpec("read_file", "read", {"type": "object"}, lambda: "contents")],
        "model": "gpt-4o", "max_tokens": 100, "max_iterations": 4,
        "submit_tool_name": "submit_handoff", "submit_tool_description": "submit",
        "submit_tool_schema": {"type": "object"},
    }
    return provider.run_agent(**{**arguments, **overrides})


def _usage(backend):
    if backend == "openai":
        return {"prompt_tokens": 100, "completion_tokens": 10}
    return {"input_tokens": 100, "output_tokens": 10}


@pytest.mark.parametrize("backend", ["openai"])
def test_openai_accumulates_normalized_usage_and_cached_tokens(provider_api, backend):
    provider, api = provider_api
    api.side_effect = [
        _response(backend, "read_file", {
            "prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110,
            "prompt_tokens_details": {"cached_tokens": 30},
        }),
        _response(backend, "read_file", {
            "prompt_tokens": 200, "completion_tokens": 20,
            "prompt_tokens_details": {"cached_tokens": 80},
        }),
        _response(backend, "submit_handoff", {
            "prompt_tokens": 300, "completion_tokens": 30,
            "prompt_tokens_details": None,
        }),
    ]

    run = _run(provider)

    assert run.usage == {
        "input_tokens": 600, "output_tokens": 60, "cache_read_input_tokens": 110,
    }
    assert run.model == "gpt-4o"
    assert run.submission == {}
    assert api.call_count == 3
    assert run.provider == "openai"
    assert cost_summary(run.model, run.usage, run.provider) == CostSummary(
        0.001825, False, {"cache_read_input_tokens": 110},
    )


@pytest.mark.parametrize("backend", ["anthropic"])
def test_anthropic_accumulates_usage_including_cache_writes(provider_api, backend):
    provider, api = provider_api
    api.side_effect = [
        _response(backend, "read_file", {
            "input_tokens": 100, "output_tokens": 10,
            "cache_read_input_tokens": 30, "cache_creation_input_tokens": 80,
        }),
        _response(backend, "read_file", {
            "input_tokens": 200, "output_tokens": 20,
            "cache_read_input_tokens": 50, "cache_creation_input_tokens": 10,
        }),
        _response(backend, "submit_handoff", {
            "input_tokens": 300, "output_tokens": 30,
            "cache_read_input_tokens": None, "cache_creation_input_tokens": None,
        }),
    ]

    run = _run(provider, model="claude-sonnet-4-6")

    assert run.usage == {
        "input_tokens": 600, "output_tokens": 60,
        "cache_read_input_tokens": 80, "cache_creation_input_tokens": 90,
    }
    assert run.model == "claude-sonnet-4-6"
    assert run.provider == "anthropic"
    assert run.submission == {}
    assert api.call_count == 3
    assert cost_summary(run.model, run.usage, run.provider) == CostSummary(
        0.0027, False, {"cache_read_input_tokens": 80, "cache_creation_input_tokens": 90},
    )


@pytest.mark.parametrize("terminal", ["submit_handoff", None, "read_file"])
def test_usage_survives_terminal_response_without_usage(backend, provider_api, terminal):
    provider, api = provider_api
    api.side_effect = [
        _response(backend, "read_file", _usage(backend)),
        _response(backend, terminal),
    ]

    run = _run(provider, max_iterations=2)

    assert run.usage["input_tokens"] == 100
    assert run.usage["output_tokens"] == 10
    assert run.model == "gpt-4o"
    assert run.submission == ({} if terminal == "submit_handoff" else None)
    assert api.call_count == 2


@pytest.mark.parametrize("terminal", [None, "read_file"])
def test_all_usage_is_counted_without_submission(backend, provider_api, terminal):
    provider, api = provider_api
    api.side_effect = [
        _response(backend, "read_file", _usage(backend)),
        _response(backend, terminal, _usage(backend)),
    ]

    run = _run(provider, max_iterations=2)

    assert run.usage["input_tokens"] == 200
    assert run.usage["output_tokens"] == 20
    assert run.submission is None
    assert run.model == "gpt-4o"
    assert api.call_count == 2


@pytest.mark.parametrize("backend", ["openai"])
@pytest.mark.parametrize("choices", [[], [{}], [None], [{"message": None}]])
def test_openai_preserves_usage_when_response_has_no_valid_choice(provider_api, choices):
    provider, api = provider_api
    api.return_value = {
        "choices": choices, "usage": {"prompt_tokens": 100, "completion_tokens": 10},
    }

    run = _run(provider)

    assert run.usage == {"input_tokens": 100, "output_tokens": 10, "cache_read_input_tokens": 0}
    assert run.model == "gpt-4o"
    assert run.submission is None
    assert run.stop_reason.startswith("provider_error:")
    api.assert_called_once()


@pytest.mark.parametrize("backend", ["openai"])
def test_openai_preserves_usage_on_invalid_json_response(provider_api):
    provider, api = provider_api
    api.side_effect = [
        _response("openai", "read_file", _usage("openai")),
        json.JSONDecodeError("invalid response", "", 0),
    ]

    run = _run(provider)

    assert run.usage == {"input_tokens": 100, "output_tokens": 10, "cache_read_input_tokens": 0}
    assert run.stop_reason == "provider_error:JSONDecodeError"
    assert run.model == "gpt-4o"
    assert run.submission is None


@pytest.mark.parametrize("successful_calls", [0, 1, 2])
def test_request_failure_preserves_received_usage(backend, provider_api, successful_calls):
    provider, api = provider_api
    error = httpx.ReadTimeout("offline failure") if backend == "openai" else FakeAPIError("offline failure")
    api.side_effect = [
        *[_response(backend, "read_file", _usage(backend)) for _ in range(successful_calls)],
        error,
    ]

    run = _run(provider)

    assert run.usage.get("input_tokens", 0) == successful_calls * 100
    assert run.usage.get("output_tokens", 0) == successful_calls * 10
    assert run.model == "gpt-4o"
    assert run.submission is None
    assert run.stop_reason == f"provider_error:{type(error).__name__}"
    assert api.call_count == successful_calls + 1


def test_tool_failure_does_not_lose_iteration_usage(backend, provider_api):
    provider, api = provider_api
    api.side_effect = [
        _response(backend, "read_file", _usage(backend)),
        _response(backend, "submit_handoff", _usage(backend)),
    ]
    tool = ToolSpec("read_file", "read", {}, Mock(side_effect=ToolError("denied")))

    run = _run(provider, tools=[tool])

    assert run.usage["input_tokens"] == 200
    assert run.usage["output_tokens"] == 20
    assert run.submission == {}


def test_runs_do_not_share_usage_or_model(backend, provider_api):
    provider, api = provider_api
    api.return_value = _response(backend, "submit_handoff", _usage(backend))

    first = _run(provider, model="first-model")
    second = _run(provider, model="second-model")

    assert first.usage == second.usage
    assert first.usage is not second.usage
    assert (first.model, second.model) == ("first-model", "second-model")


def test_zero_iterations_still_attributes_model(backend, provider_api):
    provider, api = provider_api

    run = _run(provider, max_iterations=0)

    assert run == AgentRun(model="gpt-4o", provider=backend)
    api.assert_not_called()


def test_model_defaults_empty_for_existing_callers():
    assert AgentRun().model == ""


def test_mock_attributes_model_without_submission():
    provider = MockProvider({"Developer": [ScriptedTurn()]})

    assert _run(provider, model="mock-developer") == AgentRun(model="mock-developer", provider="mock")


@pytest.mark.parametrize("arguments", [None, [], [["status", "ok"]], "text", 0, False])
def test_malformed_submit_object_returns_cumulative_usage(backend, provider_api, arguments):
    provider, api = provider_api
    malformed = _response(backend, "submit_handoff", _usage(backend))
    if backend == "openai":
        malformed["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = json.dumps(arguments)
    else:
        malformed.content[0].input = arguments
    api.side_effect = [_response(backend, "read_file", _usage(backend)), malformed]

    run = _run(provider)

    expected_usage = {"input_tokens": 200, "output_tokens": 20, "cache_read_input_tokens": 0}
    if backend == "anthropic":
        expected_usage["cache_creation_input_tokens"] = 0
    assert run == AgentRun(
        transcript=run.transcript, tool_call_count=2,
        stop_reason="protocol_error:invalid_submit_arguments",
        usage=expected_usage, model="gpt-4o", provider=backend,
    )
    assert api.call_count == 2


@pytest.mark.parametrize("backend", ["openai"])
@pytest.mark.parametrize("raw", ["{broken", "", None, [], 12])
def test_openai_invalid_submit_arguments_are_terminal(provider_api, raw):
    provider, api = provider_api
    response = _response("openai", "submit_handoff", _usage("openai"))
    response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = raw
    api.return_value = response

    run = _run(provider)

    assert run.submission is None
    assert run.usage == {"input_tokens": 100, "output_tokens": 10, "cache_read_input_tokens": 0}
    assert run.stop_reason == "protocol_error:invalid_submit_arguments"
    api.assert_called_once()


def test_openai_compatible_endpoint_does_not_claim_openai_billing(monkeypatch):
    provider = OpenAICompatibleProvider(base_url="https://gateway.invalid/v1", api_key="test-key")
    monkeypatch.setattr(provider, "_post", Mock(return_value=_response("openai", "submit_handoff", _usage("openai"))))

    run = _run(provider)

    assert run.provider == "openai-compatible"
    assert cost_summary(run.model, run.usage, run.provider) == CostSummary(
        0.0, False, {"input_tokens": 100, "output_tokens": 10},
    )


def test_openai_adapter_honors_explicit_local_billing(monkeypatch):
    class ExplicitLocalProvider(OpenAICompatibleProvider):
        billing_provider = "local"

    provider = ExplicitLocalProvider(base_url="http://localhost:11434/v1", api_key="local")
    monkeypatch.setattr(provider, "_post", Mock(return_value=_response("openai", "submit_handoff", _usage("openai"))))

    run = _run(provider, model="local-model")

    assert run.provider == "local"
    assert cost_summary(run.model, run.usage, run.provider) == CostSummary(0.0, True)
