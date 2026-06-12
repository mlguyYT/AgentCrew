"""Cost estimation + daily-budget tracking.

Two surfaces:

  1. **Pre-run preview** — given the routing + per-role models + role files,
     estimate input/output tokens and multiply by the model's published
     rates. Block when the estimated cost exceeds the project's
     `per_run_block_usd`; warn when over `per_run_warn_usd`.

  2. **Post-run accounting** — after each role runs, the provider returns
     `usage` (actual input/output tokens). We compute the real USD and
     persist it to `.agent-state/budget-history.jsonl` so the daily cap
     stays accurate across many runs.

This isn't an accountant; it's a guardrail. The estimates are deliberately
rough (chars-per-token ≈ 4) — startups need "is this $0.50 or $5?", not
"is it $0.4283 or $0.4287?".
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .routing import Routing


# Published per-million-token rates (USD). Keep additive: an unknown model
# defaults to (0, 0) which means "no estimated cost" rather than blocking.
# Local models (Ollama, vLLM, etc.) → also (0, 0).
MODEL_RATES: dict[str, tuple[float, float]] = {
    # OpenAI-compatible hosted examples
    "gpt-4o":            (2.5, 10.0),
    "gpt-4o-mini":       (0.15, 0.60),
    "gpt-4.1":           (2.0, 8.0),
    "gpt-4.1-mini":      (0.4, 1.6),
    "o1":                (15.0, 60.0),
    "o1-mini":           (3.0, 12.0),
    # Anthropic-family examples
    "claude-opus-4-7":   (5.0, 25.0),
    "claude-opus-4-6":   (5.0, 25.0),
    "claude-opus-4-5":   (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-4-5":  (1.0, 5.0),
    # Anything starting with "mock-" or "local" → zero cost
}


def _rates_for(model: str) -> tuple[float, float]:
    """Return (input_per_1m, output_per_1m) USD for the model. Unknown → (0, 0)."""
    if model in MODEL_RATES:
        return MODEL_RATES[model]
    lower = model.lower()
    if lower.startswith("mock-") or lower in ("mock", "local"):
        return (0.0, 0.0)
    # Local Ollama / vLLM model names like "qwen2.5-coder:32b", "llama3.3:70b"
    # → zero cost (running on the user's hardware).
    if ":" in model and not model.startswith("gpt-") and not model.startswith("claude-"):
        return (0.0, 0.0)
    return (0.0, 0.0)


def _est_tokens(chars: int) -> int:
    """Rough char-to-token heuristic. 4 chars/token is the common rule of thumb."""
    return max(1, chars // 4)


@dataclass
class RoleEstimate:
    role: str
    model: str
    input_tokens: int
    output_tokens: int
    input_usd: float
    output_usd: float
    total_usd: float

    @classmethod
    def compute(
        cls,
        *,
        role: str,
        model: str,
        system_prompt_chars: int,
        prior_handoff_count: int,
        gate_section_chars: int,
        max_output_tokens: int,
    ) -> "RoleEstimate":
        in_rate, out_rate = _rates_for(model)
        # Approximate input prompt size: system prompt + routing context (~600 chars)
        # + prior handoffs (~400 chars each) + gate playbook text + tools schema (~1500 chars).
        input_chars = (
            system_prompt_chars
            + 600
            + prior_handoff_count * 400
            + gate_section_chars
            + 1500
        )
        input_tokens = _est_tokens(input_chars)
        # Roles rarely use their full max_tokens budget. 60% is a reasonable
        # central estimate for completed handoffs.
        output_tokens = max(1, int(max_output_tokens * 0.6))
        input_usd = input_tokens * in_rate / 1_000_000
        output_usd = output_tokens * out_rate / 1_000_000
        return cls(
            role=role,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_usd=input_usd,
            output_usd=output_usd,
            total_usd=input_usd + output_usd,
        )


@dataclass
class RunEstimate:
    per_role: list[RoleEstimate] = field(default_factory=list)
    total_usd: float = 0.0
    has_unknown_model: bool = False

    def to_dict(self) -> dict:
        return {
            "per_role": [
                {
                    "role": e.role,
                    "model": e.model,
                    "input_tokens": e.input_tokens,
                    "output_tokens": e.output_tokens,
                    "total_usd": round(e.total_usd, 4),
                }
                for e in self.per_role
            ],
            "total_usd": round(self.total_usd, 4),
        }

    def render_table(self) -> str:
        lines = [
            "  Role                          Model                    Est tokens   Est USD",
            "  ----                          -----                    ----------   -------",
        ]
        for e in self.per_role:
            lines.append(
                f"  {e.role:<29s} {e.model:<24s} {e.input_tokens + e.output_tokens:>10,} ${e.total_usd:>7.4f}"
            )
        lines.append(
            f"  {'':<29s} {'TOTAL':<24s} {'':>10s} ${self.total_usd:>7.4f}"
        )
        return "\n".join(lines)


def estimate_run(
    *,
    routing: Routing,
    acting_roles: list[str],
    model_for_role: dict[str, str],
    role_file_chars: dict[str, int],
    gate_section_chars_for_role: dict[str, int],
    max_tokens_per_role: dict[str, int],
) -> RunEstimate:
    """Estimate the cost of running every acting role.

    Caller passes the resolved acting roles, the model per role, the size
    of each role's system prompt (file char count), and the gate section
    size that will be injected. Output is a structured estimate the
    orchestrator and the host agent can consume.
    """
    est = RunEstimate()
    for i, role in enumerate(acting_roles):
        model = model_for_role.get(role, "")
        if not model:
            est.has_unknown_model = True
            model = "(unset)"
        sys_chars = role_file_chars.get(role, 2000)  # fall back if not pre-loaded
        gate_chars = gate_section_chars_for_role.get(role, 0)
        max_tokens = max_tokens_per_role.get(role, 8192)
        role_est = RoleEstimate.compute(
            role=role,
            model=model,
            system_prompt_chars=sys_chars,
            prior_handoff_count=i,
            gate_section_chars=gate_chars,
            max_output_tokens=max_tokens,
        )
        est.per_role.append(role_est)
        est.total_usd += role_est.total_usd
    return est


# --- Daily budget tracking ----------------------------------------------------


@dataclass
class BudgetStatus:
    daily_so_far_usd: float
    daily_cap_usd: float
    today: str

    @property
    def remaining_usd(self) -> float:
        if self.daily_cap_usd <= 0:
            return float("inf")
        return max(0.0, self.daily_cap_usd - self.daily_so_far_usd)


def _budget_log(project_dir: Path) -> Path:
    return project_dir / ".agent-state" / "budget-history.jsonl"


def _today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_daily_so_far(project_dir: Path, daily_cap_usd: float) -> BudgetStatus:
    """Sum recorded costs for today from .agent-state/budget-history.jsonl."""
    today = _today_iso()
    total = 0.0
    log_path = _budget_log(project_dir)
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("date") == today:
                try:
                    total += float(entry.get("cost_usd", 0))
                except (TypeError, ValueError):
                    continue
    return BudgetStatus(daily_so_far_usd=total, daily_cap_usd=daily_cap_usd, today=today)


def record_run_cost(project_dir: Path, *, run_id: str, cost_usd: float) -> None:
    """Append an entry to .agent-state/budget-history.jsonl."""
    log_path = _budget_log(project_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": _today_iso(),
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id": run_id,
        "cost_usd": round(cost_usd, 6),
    }
    with log_path.open("a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


# --- Block / warn decisions ---------------------------------------------------


@dataclass
class CostGate:
    """Decision the orchestrator/CLI makes after estimating cost."""

    estimate: RunEstimate
    budget: BudgetStatus
    warn: bool
    block: bool
    reason: str = ""


def decide_cost_gate(
    estimate: RunEstimate,
    budget: BudgetStatus,
    *,
    per_run_warn_usd: float,
    per_run_block_usd: float,
) -> CostGate:
    block = False
    warn = False
    reason = ""

    # Daily cap check
    if budget.daily_cap_usd > 0 and (budget.daily_so_far_usd + estimate.total_usd) > budget.daily_cap_usd:
        block = True
        reason = (
            f"This run is estimated at ${estimate.total_usd:.4f}, but the daily cap is "
            f"${budget.daily_cap_usd:.2f} and ${budget.daily_so_far_usd:.4f} has already "
            f"been spent today (${budget.remaining_usd:.4f} remaining)."
        )

    # Per-run block check (only if not already blocked by daily cap)
    if not block and per_run_block_usd > 0 and estimate.total_usd > per_run_block_usd:
        block = True
        reason = (
            f"Estimated run cost ${estimate.total_usd:.4f} exceeds the per-run block "
            f"threshold ${per_run_block_usd:.2f}."
        )

    # Warn (informational; doesn't block)
    if not block and per_run_warn_usd > 0 and estimate.total_usd > per_run_warn_usd:
        warn = True
        reason = (
            f"Estimated cost ${estimate.total_usd:.4f} exceeds the warn threshold "
            f"${per_run_warn_usd:.2f}."
        )

    return CostGate(estimate=estimate, budget=budget, warn=warn, block=block, reason=reason)


# --- Actual cost from provider usage ------------------------------------------


def actual_cost_from_usage(model: str, usage: dict) -> float:
    """Compute actual USD from provider usage stats (per AgentRun.usage)."""
    in_rate, out_rate = _rates_for(model)
    input_tokens = int(usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    return (input_tokens * in_rate + output_tokens * out_rate) / 1_000_000
