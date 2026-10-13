"""Durable continuation across a mid-workflow CEO approval gate."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from .handoff import Handoff
from .routing import Routing


_SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,80}$")
_FILENAME = "continuation.json"
_MAX_ARTIFACT_BYTES = 256_000


class ContinuationError(ValueError):
    """Raised when a continuation is invalid, missing, or already consumed."""


@dataclass(frozen=True)
class Continuation:
    source_run_id: str
    task: str
    routing: Routing
    prior_handoffs: tuple[Handoff, ...]
    pending_decision: str


def write_continuation(
    run_dir: Path,
    *,
    routing: Routing,
    handoffs: list[Handoff],
) -> Path:
    """Write the remaining workflow without duplicating completed planning."""

    remaining = routing.workflow_after_mid_workflow_human_gate()
    if not remaining:
        raise ValueError("routing has no resumable mid-workflow human gate")
    source_run_id = run_dir.name
    if not _SAFE_RUN_ID.fullmatch(source_run_id):
        raise ValueError(f"unsafe run id: {source_run_id!r}")
    payload = {
        "version": 1,
        "source_run_id": source_run_id,
        "task": routing.task,
        "routing": asdict(routing),
        "remaining_workflow": remaining,
        "pending_decision": routing.next_human_decision(),
        "prior_handoffs": [handoff.model_dump(mode="json") for handoff in handoffs],
    }
    path = run_dir / _FILENAME
    serialized = json.dumps(payload, indent=2) + "\n"
    if len(serialized.encode()) > _MAX_ARTIFACT_BYTES:
        raise ContinuationError("continuation artifact exceeds size limit")
    path.write_text(serialized)
    return path


def load_continuation(project_dir: Path, run_id: str) -> Continuation:
    """Load a continuation and route only the post-approval workflow."""

    path = _continuation_path(project_dir, run_id)
    payload = _read_payload(path, run_id)
    if payload.get("version") != 1 or payload.get("source_run_id") != run_id:
        raise ContinuationError("invalid continuation artifact")
    resumed_run_id = payload.get("resumed_run_id")
    if resumed_run_id:
        raise ContinuationError(
            f"continuation already resumed by run {resumed_run_id}"
        )

    try:
        original = Routing(**payload["routing"])
        task = str(payload["task"]).strip()
        if not task:
            raise ContinuationError("continuation has no task")
        remaining = str(payload.get("remaining_workflow", "")).strip()
        if not remaining:
            raise ContinuationError("continuation has no remaining workflow")
        handoffs = tuple(
            Handoff(**item) for item in payload.get("prior_handoffs", [])
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ContinuationError):
            raise
        raise ContinuationError("invalid continuation artifact schema") from exc
    remaining_has_gate = any(
        step.strip().casefold() == "human"
        or step.strip().casefold().startswith("human ")
        for step in remaining.split("->")[:-1]
    )
    remaining_decisions = (
        list(original.human_decisions)
        if remaining_has_gate
        else [
            decision
            for decision in original.human_decisions
            if "final approval" in decision.casefold()
        ]
    )
    resumed = replace(
        original,
        workflow=remaining,
        starting_role=_first_role(remaining),
        next_roles=[
            step.strip()
            for step in remaining.split("->")[1:]
            if step.strip()
        ],
        human_decisions=remaining_decisions,
        reasons=[
            *original.reasons,
            f"continued after CEO approval from run {run_id}",
        ],
    )
    return Continuation(
        source_run_id=run_id,
        task=task,
        routing=resumed,
        prior_handoffs=handoffs,
        pending_decision=str(
            payload.get("pending_decision") or original.next_human_decision()
        ),
    )


def mark_continuation_resumed(
    project_dir: Path,
    source_run_id: str,
    resumed_run_id: str,
) -> None:
    """Mark a completed resume so the same CEO approval cannot replay work."""

    if not _SAFE_RUN_ID.fullmatch(resumed_run_id):
        raise ContinuationError(f"invalid resumed run id: {resumed_run_id!r}")
    path = _continuation_path(project_dir, source_run_id)
    payload = _read_payload(path, source_run_id)
    existing = payload.get("resumed_run_id")
    if existing and existing != resumed_run_id:
        raise ContinuationError(f"continuation already resumed by run {existing}")
    payload["resumed_run_id"] = resumed_run_id
    payload["resumed_at"] = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )
    path.write_text(json.dumps(payload, indent=2) + "\n")


def _continuation_path(project_dir: Path, run_id: str) -> Path:
    if not _SAFE_RUN_ID.fullmatch(run_id):
        raise ContinuationError(f"invalid continuation run id: {run_id!r}")
    path = project_dir.resolve() / ".agent-state" / "runs" / run_id / _FILENAME
    if not path.is_file():
        raise ContinuationError(f"continuation not found: {run_id}")
    return path


def _read_payload(path: Path, run_id: str) -> dict:
    try:
        if path.stat().st_size > _MAX_ARTIFACT_BYTES:
            raise ContinuationError("continuation artifact exceeds size limit")
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ContinuationError(
            f"unable to read continuation artifact: {run_id}"
        ) from exc
    if not isinstance(payload, dict):
        raise ContinuationError("invalid continuation artifact schema")
    return payload


def _first_role(workflow: str) -> str:
    first = workflow.split("->", 1)[0].strip()
    if not first or first.casefold().startswith("human"):
        raise ContinuationError("continuation does not begin with an acting role")
    return first.split(" if ", 1)[0].strip()
