"""Engine-derived execution evidence for Developer completion gates.

The ledger records only bounded metadata: relative paths, command categories,
exit codes, and outcomes. It never stores file contents, command arguments, or
tool output.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .execution_commands import classify_tool_call
from .handoff import Handoff
from .tools import ToolSpec


ValidationStatus = Literal["passed", "failed", "missing"]
CompletionOutcome = Literal["passed", "limited", "rework"]
FileFingerprint = tuple[str, str]
MAX_PERSISTED_EVENTS = 100
MAX_PERSISTED_CHANGED_FILES = 200
MAX_PERSISTED_PATH_CHARS = 500


@dataclass(frozen=True)
class ToolEvidenceEvent:
    sequence: int
    tool: str
    kind: str
    succeeded: bool
    path: str | None = None
    command_name: str | None = None
    validation_kind: str | None = None
    exit_code: int | None = None
    changed: bool | None = None
    truncated: bool | None = None

    def to_dict(self) -> dict:
        data = {
            key: value
            for key, value in asdict(self).items()
            if value is not None
        }
        if self.path:
            data["path"] = clip_metadata(
                self.path,
                MAX_PERSISTED_PATH_CHARS,
            )
        if self.command_name:
            data["command_name"] = clip_metadata(self.command_name, 80)
        return data


@dataclass(frozen=True)
class ExecutionEvidence:
    events: tuple[ToolEvidenceEvent, ...]
    current_changed_files: tuple[str, ...]
    observed_changed_files: tuple[str, ...]
    inspected_before_change: bool
    validation_status: ValidationStatus
    successful_validation_kinds: tuple[str, ...]
    unresolved_validation_kinds: tuple[str, ...]

    def to_dict(self, assessment: "CompletionAssessment | None" = None) -> dict:
        persisted_events = self.events[-MAX_PERSISTED_EVENTS:]
        current_files = self.current_changed_files[
            :MAX_PERSISTED_CHANGED_FILES
        ]
        observed_files = self.observed_changed_files[
            :MAX_PERSISTED_CHANGED_FILES
        ]
        data = {
            "schema_version": 1,
            "event_count": len(self.events),
            "events_truncated": len(persisted_events) < len(self.events),
            "events": [event.to_dict() for event in persisted_events],
            "current_changed_file_count": len(self.current_changed_files),
            "current_changed_files_truncated": (
                len(current_files) < len(self.current_changed_files)
            ),
            "current_changed_files": [
                clip_metadata(path, MAX_PERSISTED_PATH_CHARS)
                for path in current_files
            ],
            "observed_changed_file_count": len(self.observed_changed_files),
            "observed_changed_files_truncated": (
                len(observed_files) < len(self.observed_changed_files)
            ),
            "observed_changed_files": [
                clip_metadata(path, MAX_PERSISTED_PATH_CHARS)
                for path in observed_files
            ],
            "inspected_before_change": self.inspected_before_change,
            "validation": {
                "status": self.validation_status,
                "successful_kinds": list(self.successful_validation_kinds),
                "unresolved_kinds": list(self.unresolved_validation_kinds),
            },
        }
        if assessment is not None:
            data["completion_gate"] = {
                "outcome": assessment.outcome,
                "reasons": list(assessment.reasons),
            }
        return data


@dataclass(frozen=True)
class CompletionAssessment:
    outcome: CompletionOutcome
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationSummary:
    status: ValidationStatus
    successful_kinds: tuple[str, ...]
    unresolved_kinds: tuple[str, ...]


def clip_metadata(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


class ExecutionRecorder:
    """Wrap ToolSpec handlers and collect safe execution metadata."""

    def __init__(
        self,
        project_root: Path | None = None,
        initial_fingerprints: dict[str, FileFingerprint | None] | None = None,
    ) -> None:
        self.project_root = project_root.resolve() if project_root else None
        self.events: list[ToolEvidenceEvent] = []
        self._initial_fingerprints = (
            initial_fingerprints if initial_fingerprints is not None else {}
        )

    def instrument(self, tools: list[ToolSpec]) -> list[ToolSpec]:
        instrumented: list[ToolSpec] = []
        for spec in tools:
            instrumented.append(
                ToolSpec(
                    name=spec.name,
                    description=spec.description,
                    input_schema=spec.input_schema,
                    handler=self._handler(spec),
                )
            )
        return instrumented

    def _handler(self, spec: ToolSpec):
        def invoke(**inputs):
            sequence = len(self.events) + 1
            kind, path, command_name, validation_kind = classify_tool_call(
                spec.name, inputs, self.project_root
            )
            before_fingerprint = (
                _file_fingerprint(self.project_root, path)
                if kind == "mutation"
                else None
            )
            if kind == "mutation" and path:
                self._initial_fingerprints.setdefault(path, before_fingerprint)
            try:
                result = spec.handler(**inputs)
            except Exception:
                self.events.append(
                    ToolEvidenceEvent(
                        sequence=sequence,
                        tool=spec.name,
                        kind=kind,
                        succeeded=False,
                        path=path,
                        command_name=command_name,
                        validation_kind=validation_kind,
                        changed=_changed_since(
                            before_fingerprint,
                            (
                                _file_fingerprint(self.project_root, path)
                                if kind == "mutation"
                                else None
                            ),
                        ),
                    )
                )
                raise

            exit_code = _exit_code(result) if spec.name == "bash" else None
            succeeded = exit_code in (None, 0)
            changed = _changed_since(
                before_fingerprint,
                (
                    _file_fingerprint(self.project_root, path)
                    if kind == "mutation"
                    else None
                ),
            )
            truncated = (
                "[TRUNCATED" in result
                if isinstance(result, str)
                else None
            )
            self.events.append(
                ToolEvidenceEvent(
                    sequence=sequence,
                    tool=spec.name,
                    kind=kind,
                    succeeded=succeeded,
                    path=path,
                    command_name=command_name,
                    validation_kind=validation_kind,
                    exit_code=exit_code,
                    changed=changed,
                    truncated=truncated or None,
                )
            )
            return result

        return invoke

    def net_changed_paths(self) -> set[str]:
        """Return tool-mutated paths whose final state differs from turn start."""

        return {
            path
            for path, before in self._initial_fingerprints.items()
            if _changed_since(
                before,
                _file_fingerprint(self.project_root, path),
            )
            is True
        }


def _file_fingerprint(
    project_root: Path | None,
    relative_path: str | None,
) -> FileFingerprint | None:
    if project_root is None or relative_path is None:
        return None
    path = project_root / relative_path
    if not path.exists():
        return ("missing", "")
    if not path.is_file():
        return ("non_file", "")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return ("file", digest.hexdigest())


def _changed_since(
    before: FileFingerprint | None,
    after: FileFingerprint | None,
) -> bool | None:
    if before is None or after is None:
        return None
    return before != after


def _exit_code(result: str) -> int | None:
    match = re.match(r"^exit=(-?\d+)", result)
    return int(match.group(1)) if match else None


def _status_map(status: str | None) -> dict[str, str]:
    if status is None:
        return {}
    entries: dict[str, str] = {}
    for line in status.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        entries[path] = line[:2]
    return entries


def _counts_as_project_change(path: str) -> bool:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return not (
        normalized in {".agent-state", ".git"}
        or normalized.startswith((".agent-state/", ".git/"))
    )


def build_execution_evidence(
    *,
    recorder: ExecutionRecorder,
    status_before: str | None,
    status_after: str | None,
) -> ExecutionEvidence:
    """Build a cumulative Developer ledger from tool and repository evidence."""

    before = _status_map(status_before)
    after = _status_map(status_after)
    status_changes = {
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
        and _counts_as_project_change(path)
    }
    mutation_paths = {
        path
        for path in recorder.net_changed_paths()
        if _counts_as_project_change(path)
    }
    current_changes = tuple(sorted(status_changes | mutation_paths))
    observed_changes = current_changes

    mutation_events = [
        event
        for event in recorder.events
        if event.kind in {"mutation", "operation"}
    ]
    first_mutation = min(
        (event.sequence for event in mutation_events),
        default=None,
    )
    inspected_before_change = first_mutation is None or any(
        event.kind == "inspection" and event.sequence < first_mutation
        for event in recorder.events
    )

    validation = summarize_validation(tuple(recorder.events))

    return ExecutionEvidence(
        events=tuple(recorder.events),
        current_changed_files=current_changes,
        observed_changed_files=observed_changes,
        inspected_before_change=inspected_before_change,
        validation_status=validation.status,
        successful_validation_kinds=validation.successful_kinds,
        unresolved_validation_kinds=validation.unresolved_kinds,
    )


def summarize_validation(
    events: tuple[ToolEvidenceEvent, ...],
) -> ValidationSummary:
    """Summarize post-change checks without letting failures disappear."""

    last_mutation = max(
        (
            event.sequence
            for event in events
            if event.kind in {"mutation", "operation"}
        ),
        default=0,
    )
    latest_validation: dict[str, ToolEvidenceEvent] = {}
    failed_validation_kinds = {
        event.validation_kind
        for event in events
        if (
            event.kind == "validation"
            and event.validation_kind
            and not event.succeeded
        )
    }
    for event in events:
        if (
            event.kind == "validation"
            and event.validation_kind
            and event.sequence > last_mutation
        ):
            latest_validation[event.validation_kind] = event
    unresolved = tuple(
        sorted(
            {
                kind
                for kind, event in latest_validation.items()
                if not event.succeeded
            }
            | {
                kind
                for kind in failed_validation_kinds
                if (
                    kind not in latest_validation
                    or not latest_validation[kind].succeeded
                )
            }
        )
    )
    successful = tuple(
        sorted(
            kind
            for kind, event in latest_validation.items()
            if event.succeeded
        )
    )
    if unresolved:
        validation_status: ValidationStatus = "failed"
    elif successful:
        validation_status = "passed"
    else:
        validation_status = "missing"

    return ValidationSummary(
        status=validation_status,
        successful_kinds=successful,
        unresolved_kinds=unresolved,
    )


def assess_completion(
    evidence: ExecutionEvidence,
    handoff: Handoff,
) -> CompletionAssessment:
    reasons: list[str] = []
    if not evidence.observed_changed_files:
        reasons.append("no_engine_observed_change")
    if handoff.validation_status == "failed":
        reasons.append("developer_reported_validation_failure")

    limited = False
    if evidence.validation_status == "failed":
        reasons.append("unresolved_validation_failure")
    elif evidence.validation_status == "missing":
        declared_limitation = handoff.validation_status in {
            "unavailable",
            "not_applicable",
        } and bool(handoff.validation_limitation.strip())
        if declared_limitation:
            limited = True
        else:
            reasons.append("missing_post_change_validation")

    if reasons:
        return CompletionAssessment("rework", tuple(reasons))
    if limited:
        return CompletionAssessment("limited")
    return CompletionAssessment("passed")


def enforce_completion(
    evidence: ExecutionEvidence,
    handoff: Handoff,
) -> CompletionAssessment:
    """Apply engine evidence to a Developer handoff before workflow advance."""

    assessment = assess_completion(evidence, handoff)
    if evidence.observed_changed_files:
        handoff.files = sorted(
            {
                clip_metadata(path, MAX_PERSISTED_PATH_CHARS)
                for path in (
                    set(handoff.files) | set(evidence.observed_changed_files)
                )
            }
        )[:20]

    if assessment.outcome == "passed":
        handoff.validation_status = "passed"
        handoff.validation_limitation = ""
        return assessment
    if assessment.outcome == "limited":
        return assessment

    actions = {
        "no_engine_observed_change": (
            "make the requested project change using the bounded project tools"
        ),
        "developer_reported_validation_failure": (
            "resolve the reported validation failure"
        ),
        "unresolved_validation_failure": (
            "correct each unresolved validation kind and rerun the same check"
        ),
        "missing_post_change_validation": (
            "run a focused check after the final change or declare why validation is unavailable"
        ),
    }
    requested = "; ".join(actions[reason] for reason in assessment.reasons)
    handoff.receiver = "Developer"
    handoff.decision = "rework_required"
    handoff.next_action = (requested[:297] + "...") if len(requested) > 300 else requested
    gate_evidence = (
        "AgentCrew completion gate: " + ", ".join(assessment.reasons)
    )
    handoff.evidence = [*handoff.evidence[:19], gate_evidence]
    if evidence.validation_status == "failed":
        handoff.validation_status = "failed"
    return assessment
