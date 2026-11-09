"""Direct answers share the paid execution safeguards without workflow artifacts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .agents import build_agent
from .config import ProjectConfig
from .cost import CostGate, decide_cost_gate, load_daily_so_far
from .provider import Provider
from .run_accounting import finalize_accounting
from .tools import build_tools
from .agentcrew_root import AgentCrewRoot

if TYPE_CHECKING:
    from .orchestrator import TeamRun


def run_direct_answer(
    state: TeamRun, *, root: AgentCrewRoot, provider: Provider,
    model: str, config: ProjectConfig | None, cost_approver: Callable[[CostGate], bool],
) -> TeamRun:
    budget = load_daily_so_far(state.project_dir, config.budget.daily_max_usd if config else 0.0)
    gate = decide_cost_gate(
        state.cost_estimate, budget,
        per_run_warn_usd=config.budget.per_run_warn_usd if config else 0.0,
        per_run_block_usd=config.budget.per_run_block_usd if config else 0.0,
    )
    state.next_owner = "human"
    if (gate.warn or gate.block) and not cost_approver(gate):
        state.final_decision = "cost_rejected_by_human" if gate.block else "cost_warn_rejected_by_human"
        return state
    agent = build_agent(root, "Advisor", model)
    result = provider.run_agent(
        role="Advisor", system_prompt=agent.system_prompt(),
        user_message=(
            f"## User's question\n\n{state.task}\n\n"
            "Answer the question without changing project files. Read only relevant "
            "context, then call submit_answer exactly once."
        ),
        tools=build_tools("Advisor", state.project_dir), model=model,
        max_tokens=agent.max_tokens, max_iterations=agent.max_iterations,
        submit_tool_name="submit_answer", submit_tool_description="Submit the direct answer.",
        submit_tool_schema={"type": "object", "properties": {"answer": {
            "type": "string", "minLength": 1, "maxLength": 8000,
        }}, "required": ["answer"]},
    )
    result.model = model
    state.agent_runs.append(result)
    answer = result.submission.get("answer") if isinstance(result.submission, dict) else None
    if not isinstance(answer, str) or not answer.strip() or len(answer) > 8000:
        state.final_decision = "direct_answer_or_advisory_protocol_failure"
    else:
        state.direct_answer = answer
        state.final_decision = "answered"
    finalize_accounting(state)
    return state
