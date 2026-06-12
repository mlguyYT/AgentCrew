"""Opt-in anonymous telemetry → `.agent-state/telemetry.jsonl`.

Records per-run metrics that are useful for trend tracking but contain
no task content, no file paths, no API keys, no model strings (only
model family / family-family).

Opt-in only. Enabled when `.agentcrew/config.yaml` has:

    telemetry:
      enabled: true

The file is local. Nothing is sent over the network. Aggregation into a
community dashboard is future work; this is the schema and capture path.

Privacy rules:
  - NO task text
  - NO file paths
  - NO absolute paths anywhere
  - NO secrets (the sensitive-pattern filter from save-session.sh applies)
  - Model strings reduced to a family (e.g. claude-opus-4-7 → "claude-opus")
  - User identifiers omitted
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


_TELEMETRY_FILE = "telemetry.jsonl"


def _family_for_model(model: str) -> str:
    """Reduce a model string to a coarse family. Used so the captured metric
    doesn't leak rate-bearing fingerprints or vendor-internal version codes.
    """
    if not model:
        return "unset"
    m = model.lower()
    if m.startswith("claude-opus"):
        return "claude-opus"
    if m.startswith("claude-sonnet"):
        return "claude-sonnet"
    if m.startswith("claude-haiku"):
        return "claude-haiku"
    if m.startswith("gpt-4o-mini"):
        return "gpt-4o-mini"
    if m.startswith("gpt-4"):
        return "gpt-4"
    if m.startswith("o1"):
        return "o1"
    if m.startswith("mock-") or m == "mock":
        return "mock"
    # Local Ollama models like qwen2.5-coder:32b → "local"
    if ":" in m:
        return "local"
    return "other"


def _classify_decision(decision: str) -> str:
    """Bucket final_decision into a coarse class for trend tracking."""
    if not decision:
        return "unknown"
    d = decision.lower()
    if "ready_for_human_approval" in d or "ready_for_human_release_review" in d:
        return "approved"
    if "rework" in d:
        return "rework"
    # Check cost_ before generic rejected/blocked so cost_rejected_by_human
    # buckets correctly.
    if "cost_" in d:
        return "cost_gate"
    if "blocked" in d:
        return "blocked"
    if "rejected" in d:
        return "rejected"
    if "protocol_failure" in d or "role_file_missing" in d or "model_missing" in d:
        return "infra_failure"
    if "answered" in d:
        return "direct_answer"
    return "other"


def emit_run_event(
    project_dir: Path,
    *,
    enabled: bool,
    run_id: str,
    lane: str,
    recipe: str,
    risk: str,
    quality_profile: str,
    acting_roles_count: int,
    specialists_count: int,
    gates_count: int,
    final_decision: str,
    next_owner: str,
    estimated_cost_usd: float,
    actual_cost_usd: float,
    duration_seconds: float,
    models_by_role: dict[str, str],
) -> None:
    """Append one row of anonymized metrics. No-op when enabled=False."""
    if not enabled:
        return
    log_path = project_dir / ".agent-state" / _TELEMETRY_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id_hash": _hash(run_id),
        "lane": lane,
        "recipe": recipe,
        "risk": risk,
        "profile": quality_profile,
        "acting_roles_count": acting_roles_count,
        "specialists_count": specialists_count,
        "gates_count": gates_count,
        "final_class": _classify_decision(final_decision),
        "next_owner": next_owner,
        "estimated_cost_usd": round(estimated_cost_usd, 4),
        "actual_cost_usd": round(actual_cost_usd, 4),
        "duration_seconds": round(duration_seconds, 2),
        "model_families": sorted(set(_family_for_model(m) for m in models_by_role.values())),
    }
    with log_path.open("a") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


def _hash(s: str) -> str:
    """Short non-cryptographic hash so the run id can be correlated without
    revealing the original timestamp/uuid format. 12 hex chars is enough for
    local trend analysis."""
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def read_recent(project_dir: Path, *, limit: int = 50) -> list[dict]:
    """Return the last `limit` telemetry records (for `agentcrew audit --telemetry`)."""
    log_path = project_dir / ".agent-state" / _TELEMETRY_FILE
    if not log_path.exists():
        return []
    lines = log_path.read_text().splitlines()
    out = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
