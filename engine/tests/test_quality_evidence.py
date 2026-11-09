from agentcrew.execution_evidence import ExecutionRecorder, ToolEvidenceEvent
from agentcrew.handoff import Handoff
from agentcrew.quality_evidence import (
    build_reviewer_evidence,
    build_tester_evidence,
    enforce_reviewer_completion,
    enforce_tester_completion,
)
from agentcrew.tools import build_tools


def _handoff(sender, receiver="Human", **overrides):
    values = {
        "sender": sender,
        "receiver": receiver,
        "decision": "ready_for_human_approval",
        "next_action": "Human reviews the evidence.",
    }
    return Handoff(**{**values, **overrides})


def _recorder(*events):
    recorder = ExecutionRecorder()
    recorder.events.extend(events)
    return recorder


def test_tester_pass_requires_observed_behavior_validation():
    evidence = build_tester_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="bash",
                kind="validation",
                validation_kind="test",
                succeeded=True,
                exit_code=0,
            )
        )
    )
    handoff = _handoff("Tester")

    assessment = enforce_tester_completion(
        evidence,
        handoff,
        require_behavior_validation=True,
        developer_available=True,
    )

    assert assessment.outcome == "passed"
    assert handoff.validation_status == "passed"


def test_tester_syntax_only_routes_back_to_tester():
    evidence = build_tester_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="bash",
                kind="validation",
                validation_kind="syntax",
                succeeded=True,
                exit_code=0,
            )
        )
    )
    handoff = _handoff("Tester")

    assessment = enforce_tester_completion(
        evidence,
        handoff,
        require_behavior_validation=True,
        developer_available=True,
    )

    assert assessment.reasons == ("missing_behavior_validation",)
    assert handoff.receiver == "Tester"
    assert handoff.decision == "rework_required"


def test_tester_failure_routes_to_developer():
    evidence = build_tester_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="bash",
                kind="validation",
                validation_kind="test",
                succeeded=False,
                exit_code=1,
            )
        )
    )
    handoff = _handoff("Tester")

    assessment = enforce_tester_completion(
        evidence,
        handoff,
        require_behavior_validation=True,
        developer_available=True,
    )

    assert assessment.reasons == ("observed_validation_failure",)
    assert handoff.receiver == "Developer"
    assert handoff.validation_status == "failed"


def test_tester_unrelated_suite_cannot_clear_failure_before_matching_rerun(tmp_path):
    (tmp_path / "app.py").write_text("VALUE = 1\n")
    (tmp_path / "suite_a.py").write_text(
        "import unittest\n"
        "from app import VALUE\n"
        "class SuiteA(unittest.TestCase):\n"
        "    def test_value(self):\n"
        "        self.assertEqual(VALUE, 2)\n"
    )
    (tmp_path / "suite_b.py").write_text(
        "import unittest\n"
        "class SuiteB(unittest.TestCase):\n"
        "    def test_unrelated_behavior(self):\n"
        "        self.assertEqual(2 + 2, 4)\n"
    )
    recorder = ExecutionRecorder(tmp_path)
    tester_tools = {
        tool.name: tool
        for tool in recorder.instrument(build_tools("Tester", tmp_path))
    }

    assert tester_tools["bash"].handler(
        command="python3 -m unittest suite_a"
    ).startswith("exit=1\n")
    assert tester_tools["bash"].handler(
        command="python3 -m unittest suite_b"
    ).startswith("exit=0\n")

    failed = build_tester_evidence(recorder)
    handoff = _handoff("Tester")
    assessment = enforce_tester_completion(
        failed,
        handoff,
        require_behavior_validation=True,
        developer_available=True,
    )

    assert failed.to_dict()["validation"] == {
        "status": "failed",
        "successful_kinds": ["test"],
        "unresolved_kinds": ["test"],
    }
    assert assessment.reasons == ("observed_validation_failure",)
    assert handoff.receiver == "Developer"
    assert handoff.validation_status == "failed"

    developer_tools = {
        tool.name: tool
        for tool in recorder.instrument(build_tools("Developer", tmp_path))
    }
    developer_tools["edit_file"].handler(
        path="app.py", old_string="VALUE = 1", new_string="VALUE = 2"
    )
    assert tester_tools["bash"].handler(
        command="python3 -m unittest suite_b"
    ).startswith("exit=0\n")
    assert build_tester_evidence(recorder).validation_status == "failed"

    assert tester_tools["bash"].handler(
        command='  python3  -m unittest "suite_a"  '
    ).startswith("exit=0\n")
    recovered = build_tester_evidence(recorder)
    handoff = _handoff("Tester")

    assert recovered.to_dict()["validation"] == {
        "status": "passed",
        "successful_kinds": ["test"],
        "unresolved_kinds": [],
    }
    assert enforce_tester_completion(
        recovered,
        handoff,
        require_behavior_validation=True,
        developer_available=True,
    ).outcome == "passed"
    assert handoff.validation_status == "passed"


def test_tester_can_report_a_concrete_validation_limitation():
    evidence = build_tester_evidence(_recorder())
    handoff = _handoff(
        "Tester",
        validation_status="unavailable",
        validation_limitation="The project has no executable test harness.",
    )

    assessment = enforce_tester_completion(
        evidence,
        handoff,
        require_behavior_validation=True,
        developer_available=True,
    )

    assert assessment.outcome == "limited"


def test_reviewer_pass_requires_complete_diff_when_git_is_available():
    evidence = build_reviewer_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="git_diff",
                kind="inspection",
                path="*",
                succeeded=True,
            )
        ),
        expected_changed_files=("app.py",),
    )
    handoff = _handoff("Reviewer")

    assessment = enforce_reviewer_completion(
        evidence,
        handoff,
        git_available=True,
    )

    assert assessment.outcome == "passed"
    assert evidence.missing_changed_files == ()


def test_reviewer_can_cover_complete_scope_with_targeted_diffs():
    evidence = build_reviewer_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="git_diff",
                kind="inspection",
                path="app.py",
                succeeded=True,
            ),
            ToolEvidenceEvent(
                sequence=2,
                tool="git_diff",
                kind="inspection",
                path="tests/test_app.py",
                succeeded=True,
            ),
        ),
        expected_changed_files=("app.py", "tests/test_app.py"),
    )

    assessment = enforce_reviewer_completion(
        evidence,
        _handoff("Reviewer"),
        git_available=True,
    )

    assert assessment.outcome == "passed"
    assert evidence.missing_diff_files == ()


def test_reviewer_without_inspection_self_routes_for_rework():
    evidence = build_reviewer_evidence(
        _recorder(),
        expected_changed_files=("app.py",),
    )
    handoff = _handoff("Reviewer")

    assessment = enforce_reviewer_completion(
        evidence,
        handoff,
        git_available=True,
    )

    assert assessment.reasons == ("no_observed_review_inspection",)
    assert handoff.receiver == "Reviewer"
    assert handoff.decision == "rework_required"


def test_truncated_diff_requires_targeted_changed_path_inspection():
    evidence = build_reviewer_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="git_diff",
                kind="inspection",
                path="*",
                succeeded=True,
                truncated=True,
            ),
            ToolEvidenceEvent(
                sequence=2,
                tool="read_file",
                kind="inspection",
                path="app.py",
                succeeded=True,
            ),
        ),
        expected_changed_files=("app.py", "tests/test_app.py"),
    )

    assert evidence.missing_changed_files == ("tests/test_app.py",)
    assert enforce_reviewer_completion(
        evidence,
        _handoff("Reviewer"),
        git_available=True,
    ).reasons == ("truncated_diff_paths_not_inspected",)


def test_file_reads_do_not_replace_targeted_diffs_after_truncation():
    evidence = build_reviewer_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="git_diff",
                kind="inspection",
                path="*",
                succeeded=True,
                truncated=True,
            ),
            ToolEvidenceEvent(
                sequence=2,
                tool="read_file",
                kind="inspection",
                path="app.py",
                succeeded=True,
            ),
        ),
        expected_changed_files=("app.py",),
    )

    assessment = enforce_reviewer_completion(
        evidence,
        _handoff("Reviewer"),
        git_available=True,
    )

    assert assessment.reasons == ("truncated_diff_paths_not_inspected",)


def test_targeted_diff_completes_scope_after_full_diff_truncation():
    evidence = build_reviewer_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="git_diff",
                kind="inspection",
                path="*",
                succeeded=True,
                truncated=True,
            ),
            ToolEvidenceEvent(
                sequence=2,
                tool="git_diff",
                kind="inspection",
                path="app.py",
                succeeded=True,
            ),
        ),
        expected_changed_files=("app.py",),
    )

    assert enforce_reviewer_completion(
        evidence,
        _handoff("Reviewer"),
        git_available=True,
    ).outcome == "passed"


def test_git_review_without_known_paths_still_requires_full_diff():
    evidence = build_reviewer_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="read_file",
                kind="inspection",
                path="app.py",
                succeeded=True,
            )
        ),
        expected_changed_files=(),
    )

    assert enforce_reviewer_completion(
        evidence,
        _handoff("Reviewer"),
        git_available=True,
    ).reasons == ("complete_diff_not_inspected",)


def test_truncated_read_does_not_complete_truncated_diff_scope():
    evidence = build_reviewer_evidence(
        _recorder(
            ToolEvidenceEvent(
                sequence=1,
                tool="git_diff",
                kind="inspection",
                path="*",
                succeeded=True,
                truncated=True,
            ),
            ToolEvidenceEvent(
                sequence=2,
                tool="read_file",
                kind="inspection",
                path="app.py",
                succeeded=True,
                truncated=True,
            ),
        ),
        expected_changed_files=("app.py",),
    )

    assert evidence.missing_changed_files == ("app.py",)
