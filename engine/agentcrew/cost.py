"""Cost estimation + daily-budget tracking.

Two surfaces:

  1. **Pre-run preview** — given the routing + per-role models + role files,
     estimate input/output tokens and multiply by the model's published
     rates. Block when the estimated cost exceeds the project's
     `per_run_block_usd`; warn when over `per_run_warn_usd`.

  2. **Post-run accounting** — after each role runs, the provider returns
     `usage` (actual input/output and cache tokens). We persist the known
     USD subtotal and any pricing uncertainty to the daily budget ledger.
     Unresolved spend prevents verification of a later daily cap.

This isn't an accountant; it's a guardrail. The estimates are deliberately
rough (chars-per-token ≈ 4) — startups need "is this $0.50 or $5?", not
"is it $0.4283 or $0.4287?".
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .routing import Routing
from .state_paths import project_state_path


# Published per-million-token rates (USD). Unknown pricing is distinct from
# known zero-cost mock/local conventions and requires explicit cost approval.
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
    # "mock", "mock-*", and "local" are explicit zero-cost conventions.
}


def _rates_for(model: str) -> tuple[float, float] | None:
    """Return per-million-token USD rates, or None when pricing is unknown."""
    if model in MODEL_RATES:
        return MODEL_RATES[model]
    lower = model.lower()
    if lower.startswith("mock-") or lower in ("mock", "local"):
        return (0.0, 0.0)
    return None


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
    pricing_known: bool = True

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
        in_rate, out_rate = _rates_for(model) or (0.0, 0.0)
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
            "has_unknown_model": self.has_unknown_model,
        }

    def render_table(self) -> str:
        lines = [
            "  Role                          Model                    Est tokens   Est USD",
            "  ----                          -----                    ----------   -------",
        ]
        for e in self.per_role:
            cost = f"${e.total_usd:>7.4f}" if e.pricing_known else " UNKNOWN"
            lines.append(
                f"  {e.role:<29s} {e.model:<24s} {e.input_tokens + e.output_tokens:>10,} {cost}"
            )
        total_label = "KNOWN TOTAL" if self.has_unknown_model else "TOTAL"
        lines.append(
            f"  {'':<29s} {total_label:<24s} {'':>10s} ${self.total_usd:>7.4f}"
        )
        if self.has_unknown_model:
            lines.append("  Unknown pricing: total excludes unpriced models; explicit approval required.")
        return "\n".join(lines)


def estimate_run(
    *,
    routing: Routing,
    acting_roles: list[str],
    model_for_role: dict[str, str],
    role_file_chars: dict[str, int],
    gate_section_chars_for_role: dict[str, int],
    max_tokens_per_role: dict[str, int],
    prior_handoff_count: int = 0,
) -> RunEstimate:
    """Estimate the cost of running every acting role.

    Caller passes the resolved acting roles, the model per role, the size
    of each role's system prompt (file char count), and the gate section
    size that will be injected. Output is a structured estimate the
    orchestrator and the host agent can consume.
    """
    est = RunEstimate()
    for i, role in enumerate(acting_roles):
        model = model_for_role.get(role, "") or "(unset)"
        if _rates_for(model) is None:
            est.has_unknown_model = True
        sys_chars = role_file_chars.get(role, 2000)  # fall back if not pre-loaded
        gate_chars = gate_section_chars_for_role.get(role, 0)
        max_tokens = max_tokens_per_role.get(role, 8192)
        role_est = RoleEstimate.compute(
            role=role,
            model=model,
            system_prompt_chars=sys_chars,
            prior_handoff_count=prior_handoff_count + i,
            gate_section_chars=gate_chars,
            max_output_tokens=max_tokens,
        )
        role_est.pricing_known = _rates_for(model) is not None
        est.per_role.append(role_est)
        est.total_usd += role_est.total_usd
    return est


# --- Daily budget tracking ----------------------------------------------------


@dataclass
class BudgetStatus:
    daily_so_far_usd: float
    daily_cap_usd: float
    today: str
    has_unresolved_spend: bool = False

    @property
    def remaining_usd(self) -> float:
        if self.daily_cap_usd <= 0:
            return float("inf")
        if self.has_unresolved_spend:
            return 0.0
        return max(0.0, self.daily_cap_usd - self.daily_so_far_usd)


def _budget_log(project_dir: Path) -> Path:
    return project_state_path(project_dir, "budget-history.jsonl")


def _today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_daily_so_far(project_dir: Path, daily_cap_usd: float) -> BudgetStatus:
    """Sum today's known costs, flagging unresolved or unreadable spend."""
    today = _today_iso()
    total = 0.0
    unresolved = False
    log_path = _budget_log(project_dir)
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                unresolved = True
                continue
            if not isinstance(entry, dict) or not isinstance(entry.get("date"), str):
                unresolved = True
                continue
            if entry.get("date") == today:
                unresolved |= entry.get("pricing_known", True) is not True
                try:
                    cost = float(entry["cost_usd"])
                    if isinstance(entry["cost_usd"], bool) or not math.isfinite(cost) or cost < 0:
                        raise ValueError("Invalid recorded cost")
                    total += cost
                except (KeyError, TypeError, ValueError):
                    unresolved = True
                    continue
    return BudgetStatus(
        daily_so_far_usd=total, daily_cap_usd=daily_cap_usd, today=today,
        has_unresolved_spend=unresolved,
    )


def record_run_cost(
    project_dir: Path, *, run_id: str, cost_usd: float, pricing_known: bool = True,
    unresolved_usage: list[dict] | None = None,
) -> None:
    """Record the known subtotal, even when unresolved spend has no USD value.

    Legacy callers/entries are fully priced by default. New callers must pass
    the pricing summary's flag, including for an unresolved zero subtotal.
    """
    if not math.isfinite(cost_usd) or cost_usd < 0:
        raise ValueError("Recorded cost must be finite and nonnegative")
    log_path = _budget_log(project_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": _today_iso(),
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id": run_id,
        "cost_usd": round(cost_usd, 6),
        "pricing_known": pricing_known,
    }
    if unresolved_usage:
        entry["unresolved_usage"] = unresolved_usage
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

    if estimate.has_unknown_model:
        block = True
        warn = False
        unknown_reason = (
            "Model pricing is unknown for one or more roles. The estimate excludes "
            "these costs, so budget limits cannot be verified. Explicit cost approval "
            "is required before running."
        )
        reason = f"{reason} {unknown_reason}".strip()

    if budget.daily_cap_usd > 0 and budget.has_unresolved_spend:
        block = True
        warn = False
        reason = (
            f"{reason} The daily cap cannot be verified because recorded spend "
            "has unresolved pricing or invalid ledger entries. Explicit cost "
            "approval is required before running."
        ).strip()

    return CostGate(estimate=estimate, budget=budget, warn=warn, block=block, reason=reason)


# --- Actual cost from provider usage ------------------------------------------


@dataclass(frozen=True)
class CostSummary:
    """Known USD subtotal and token counters whose price remains unresolved.

    A zero known subtotal is not a claim that an unpriced run was free.
    """

    known_cost_usd: float
    pricing_known: bool
    unresolved_usage: dict[str, int] = field(default_factory=dict)


def cost_summary(model: str, usage: dict, provider: str = "") -> CostSummary:
    """Price ordinary tokens, retaining uncertainty about cache/billing rates.

    No cache rates are assumed. For OpenAI, cached reads are a subset of
    input_tokens: exclude them from the known subtotal instead of charging
    them twice. Anthropic cache reads and creations are separate counters.
    An omitted provider preserves model-table pricing for legacy callers;
    compatible endpoints must not inherit another vendor's billing rates.
    """
    input_tokens = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0)
    output_tokens = int(usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0)
    cache_read = int(usage.get(
        "cache_read_input_tokens",
        (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0),
    ) or 0)
    cache_write = int(usage.get("cache_creation_input_tokens", 0) or 0)
    counters = {
        "input_tokens": input_tokens, "output_tokens": output_tokens,
        "cache_read_input_tokens": cache_read, "cache_creation_input_tokens": cache_write,
    }
    if any(value < 0 for value in counters.values()):
        raise ValueError("Usage counters must be nonnegative")
    if provider in {"mock", "local"}:
        return CostSummary(0.0, True)
    rates = _rates_for(model)
    family = "anthropic" if model.startswith("claude-") else "openai"
    if rates is None or (provider and provider != family):
        return CostSummary(0.0, False, {key: value for key, value in counters.items() if value})
    if rates == (0.0, 0.0):
        return CostSummary(0.0, not provider, {} if not provider else counters)
    unresolved = {key: value for key, value in counters.items() if key.startswith("cache_") and value}
    if family == "openai":
        if cache_read > input_tokens:
            return CostSummary(0.0, False, {key: value for key, value in counters.items() if value})
        input_tokens -= cache_read
    in_rate, out_rate = rates
    known_cost = (input_tokens * in_rate + output_tokens * out_rate) / 1_000_000
    return CostSummary(known_cost, not unresolved, unresolved)


def actual_cost_from_usage(model: str, usage: dict, provider: str = "") -> float | None:
    """Return numeric USD only for fully priced usage; otherwise return None.

    Use cost_summary to retain a partially priced subtotal and its uncertainty.
    """
    summary = cost_summary(model, usage, provider)
    return summary.known_cost_usd if summary.pricing_known else None
