"""Engine-observed evidence gates for Tester and Reviewer turns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .execution_evidence import (
    MAX_PERSISTED_CHANGED_FILES,
    MAX_PERSISTED_EVENTS,
    MAX_PERSISTED_PATH_CHARS,
    ExecutionRecorder,
    ToolEvidenceEvent,
    clip_metadata,
    summarize_validation,
)
from .handoff import Handoff


QualityOutcome = Literal["passed", "limited", "rework"]


@dataclass(frozen=True)
class QualityAssessment:
    outcome: QualityOutcome
    reasons: tuple[str, ...] = ()


def _bounded_paths(paths: tuple[str, ...]) -> list[str]:
    return [
        clip_metadata(path, MAX_PERSISTED_PATH_CHARS)
        for path in paths[:MAX_PERSISTED_CHANGED_FILES]
    ]


@dataclass(frozen=True)
class TesterEvidence:
    events: tuple[ToolEvidenceEvent, ...]
    inspected_paths: tuple[str, ...]
    validation_status: Literal["passed", "failed", "missing"]
    successful_validation_kinds: tuple[str, ...]
    unresolved_validation_kinds: tuple[str, ...]

    def to_dict(self, assessment: QualityAssessment | None = None) -> dict:
        data = {
            "schema_version": 1,
            "role": "Tester",
            **_event_payload(self.events),
            "inspected_paths": _bounded_paths(self.inspected_paths),
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
class ReviewerEvidence:
    events: tuple[ToolEvidenceEvent, ...]
    expected_changed_files: tuple[str, ...]
    inspected_paths: tuple[str, ...]
    diff_inspected_paths: tuple[str, ...]
    missing_changed_files: tuple[str, ...]
    missing_diff_files: tuple[str, ...]
    full_diff_inspected: bool
    full_diff_truncated: bool
    inspection_count: int

    def to_dict(self, assessment: QualityAssessment | None = None) -> dict:
        data = {
            "schema_version": 1,
            "role": "Reviewer",
            **_event_payload(self.events),
            "expected_changed_files": _bounded_paths(
                self.expected_changed_files
            ),
            "inspected_paths": _bounded_paths(self.inspected_paths),
            "diff_inspected_paths": _bounded_paths(
                self.diff_inspected_paths
            ),
            "missing_changed_files": _bounded_paths(
                self.missing_changed_files
            ),
            "missing_diff_files": _bounded_paths(self.missing_diff_files),
            "full_diff_inspected": self.full_diff_inspected,
            "full_diff_truncated": self.full_diff_truncated,
            "inspection_count": self.inspection_count,
        }
        if assessment is not None:
            data["completion_gate"] = {
                "outcome": assessment.outcome,
                "reasons": list(assessment.reasons),
            }
        return data


def _event_payload(events: tuple[ToolEvidenceEvent, ...]) -> dict:
    persisted = events[-MAX_PERSISTED_EVENTS:]
    return {
        "event_count": len(events),
        "events_truncated": len(persisted) < len(events),
        "events": [event.to_dict() for event in persisted],
    }


def build_tester_evidence(recorder: ExecutionRecorder) -> TesterEvidence:
    events = tuple(recorder.events)
    validation = summarize_validation(events)
    inspected_paths = tuple(
        sorted(
            {
                event.path
                for event in events
                if (
                    event.kind == "inspection"
                    and event.succeeded
                    and event.path
                    and event.path != "*"
                )
            }
        )
    )
    return TesterEvidence(
        events=events,
        inspected_paths=inspected_paths,
        validation_status=validation.status,
        successful_validation_kinds=validation.successful_kinds,
        unresolved_validation_kinds=validation.unresolved_kinds,
    )


def assess_tester_completion(
    evidence: TesterEvidence,
    handoff: Handoff,
    *,
    require_behavior_validation: bool,
) -> QualityAssessment:
    reasons: list[str] = []
    if handoff.validation_status == "failed":
        reasons.append("tester_reported_validation_failure")
    if evidence.validation_status == "failed":
        reasons.append("observed_validation_failure")

    declared_limitation = (
        handoff.validation_status in {"unavailable", "not_applicable"}
        and bool(handoff.validation_limitation.strip())
    )
    limited = False
    if evidence.validation_status == "missing":
        if declared_limitation:
            limited = True
        else:
            reasons.append("missing_validation_evidence")
    elif (
        evidence.validation_status == "passed"
        and require_behavior_validation
        and "test" not in evidence.successful_validation_kinds
    ):
        if declared_limitation:
            limited = True
        else:
            reasons.append("missing_behavior_validation")

    if reasons:
        return QualityAssessment("rework", tuple(reasons))
    if limited:
        return QualityAssessment("limited")
    return QualityAssessment("passed")


def enforce_tester_completion(
    evidence: TesterEvidence,
    handoff: Handoff,
    *,
    require_behavior_validation: bool,
    developer_available: bool,
) -> QualityAssessment:
    assessment = assess_tester_completion(
        evidence,
        handoff,
        require_behavior_validation=require_behavior_validation,
    )
    if assessment.outcome == "passed":
        handoff.validation_status = "passed"
        handoff.validation_limitation = ""
        return assessment
    if assessment.outcome == "limited":
        return assessment

    implementation_failure = any(
        reason
        in {
            "tester_reported_validation_failure",
            "observed_validation_failure",
        }
        for reason in assessment.reasons
    )
    handoff.receiver = (
        "Developer"
        if implementation_failure and developer_available
        else "Human"
        if implementation_failure
        else "Tester"
    )
    handoff.decision = "rework_required"
    handoff.next_action = _tester_next_action(assessment.reasons)
    handoff.evidence = [
        *handoff.evidence[:19],
        "AgentCrew Tester gate: " + ", ".join(assessment.reasons),
    ]
    if evidence.validation_status == "failed":
        handoff.validation_status = "failed"
    return assessment


def _tester_next_action(reasons: tuple[str, ...]) -> str:
    if "observed_validation_failure" in reasons:
        return "Developer resolves the observed failure, then Tester reruns the same validation kind."
    if "tester_reported_validation_failure" in reasons:
        return "Developer resolves the reported failure, then Tester reruns validation."
    if "missing_behavior_validation" in reasons:
        return "Tester runs a focused behavior-level check or records why it is unavailable."
    return "Tester runs an authoritative project check or records why validation is unavailable."


def build_reviewer_evidence(
    recorder: ExecutionRecorder,
    *,
    expected_changed_files: tuple[str, ...],
) -> ReviewerEvidence:
    events = tuple(recorder.events)
    inspections = tuple(
        event
        for event in events
        if event.kind == "inspection" and event.succeeded
    )
    inspected_paths = tuple(
        sorted(
            {
                event.path
                for event in inspections
                if (
                    event.path
                    and event.path != "*"
                    and not event.truncated
                )
            }
        )
    )
    full_diff_events = tuple(
        event
        for event in inspections
        if event.tool == "git_diff" and event.path == "*"
    )
    full_diff_inspected = bool(full_diff_events)
    full_diff_truncated = bool(
        full_diff_events and full_diff_events[-1].truncated
    )
    expected = tuple(sorted(set(expected_changed_files)))
    diff_inspected_paths = tuple(
        sorted(
            {
                event.path
                for event in inspections
                if (
                    event.tool == "git_diff"
                    and event.path
                    and event.path != "*"
                    and not event.truncated
                )
            }
        )
    )
    covered = (
        set(expected)
        if full_diff_inspected and not full_diff_truncated
        else set(expected) & set(inspected_paths)
    )
    missing = tuple(sorted(set(expected) - covered))
    diff_covered = (
        set(expected)
        if full_diff_inspected and not full_diff_truncated
        else set(expected) & set(diff_inspected_paths)
    )
    missing_diff = tuple(sorted(set(expected) - diff_covered))
    return ReviewerEvidence(
        events=events,
        expected_changed_files=expected,
        inspected_paths=inspected_paths,
        diff_inspected_paths=diff_inspected_paths,
        missing_changed_files=missing,
        missing_diff_files=missing_diff,
        full_diff_inspected=full_diff_inspected,
        full_diff_truncated=full_diff_truncated,
        inspection_count=len(inspections),
    )


def assess_reviewer_completion(
    evidence: ReviewerEvidence,
    *,
    git_available: bool,
) -> QualityAssessment:
    reasons: list[str] = []
    if evidence.inspection_count == 0:
        reasons.append("no_observed_review_inspection")
    elif git_available:
        complete_full_diff = (
            evidence.full_diff_inspected
            and not evidence.full_diff_truncated
        )
        if not complete_full_diff and evidence.missing_diff_files:
            reasons.append(
                "truncated_diff_paths_not_inspected"
                if evidence.full_diff_truncated
                else "complete_diff_not_inspected"
            )
        elif not complete_full_diff and not evidence.expected_changed_files:
            reasons.append("complete_diff_not_inspected")
    elif (
        evidence.expected_changed_files
        and evidence.missing_changed_files
    ):
        reasons.append("changed_paths_not_inspected")
    if reasons:
        return QualityAssessment("rework", tuple(reasons))
    return QualityAssessment("passed")


def enforce_reviewer_completion(
    evidence: ReviewerEvidence,
    handoff: Handoff,
    *,
    git_available: bool,
) -> QualityAssessment:
    assessment = assess_reviewer_completion(
        evidence,
        git_available=git_available,
    )
    if assessment.outcome == "passed":
        return assessment

    handoff.receiver = "Reviewer"
    handoff.decision = "rework_required"
    handoff.next_action = _reviewer_next_action(assessment.reasons)
    handoff.evidence = [
        *handoff.evidence[:19],
        "AgentCrew Reviewer gate: " + ", ".join(assessment.reasons),
    ]
    return assessment


def _reviewer_next_action(reasons: tuple[str, ...]) -> str:
    if "complete_diff_not_inspected" in reasons:
        return "Reviewer inspects the complete Git diff before submitting a recommendation."
    if "truncated_diff_paths_not_inspected" in reasons:
        return "Reviewer runs a targeted Git diff for each path omitted by the truncated diff."
    if "changed_paths_not_inspected" in reasons:
        return "Reviewer reads every engine-observed changed path before recommending."
    return "Reviewer inspects the actual change before submitting a recommendation."
