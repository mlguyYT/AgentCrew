import json

from agentcrew.execution_commands import classify_tool_call
from agentcrew.execution_evidence import (
    ExecutionEvidence,
    ExecutionRecorder,
    ToolEvidenceEvent,
    assess_completion,
    build_execution_evidence,
    enforce_completion,
)
from agentcrew.handoff import Handoff
from agentcrew.tools import build_tools


def _instrumented_tools(project):
    recorder = ExecutionRecorder(project)
    tools = {
        tool.name: tool
        for tool in recorder.instrument(build_tools("Developer", project))
    }
    return recorder, tools


def _handoff(**overrides):
    values = {
        "sender": "Developer",
        "receiver": "Tester",
        "decision": "ready_for_test",
        "next_action": "Tester validates the change.",
    }
    return Handoff(**{**values, **overrides})


def test_script_validation_names_use_tokens_not_substrings(tmp_path):
    project = tmp_path.resolve()

    assert classify_tool_call(
        "bash",
        {"command": "npx test:unit"},
        project,
    ) == ("validation", None, "npx", "test")
    assert classify_tool_call(
        "bash",
        {"command": "npx contest"},
        project,
    ) == ("operation", None, "npx", None)


def test_persisted_evidence_is_bounded():
    events = tuple(
        ToolEvidenceEvent(
            sequence=index,
            tool="read_file",
            kind="inspection",
            succeeded=True,
            path="x" * 600,
        )
        for index in range(1, 102)
    )
    evidence = ExecutionEvidence(
        events=events,
        current_changed_files=("y" * 600,),
        observed_changed_files=("y" * 600,),
        inspected_before_change=True,
        validation_status="missing",
        successful_validation_kinds=(),
        unresolved_validation_kinds=(),
    )

    serialized = evidence.to_dict()

    assert serialized["event_count"] == 101
    assert serialized["events_truncated"] is True
    assert len(serialized["events"]) == 100
    assert serialized["events"][0]["sequence"] == 2
    assert len(serialized["events"][0]["path"]) == 500
    assert len(serialized["observed_changed_files"][0]) == 500


def test_records_sanitized_change_and_validation_evidence(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("value = 1\n")
    recorder, tools = _instrumented_tools(project)

    tools["read_file"].handler(path="app.py")
    tools["edit_file"].handler(
        path="app.py",
        old_string="value = 1",
        new_string="value = 2",
    )
    tools["bash"].handler(command="python3 -m py_compile app.py")

    evidence = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=None,
    )
    serialized = json.dumps(evidence.to_dict())

    assert evidence.observed_changed_files == ("app.py",)
    assert evidence.inspected_before_change is True
    assert evidence.validation_status == "passed"
    assert evidence.successful_validation_kinds == ("syntax",)
    assert "value = 2" not in serialized
    assert "python3 -m py_compile app.py" not in serialized


def test_identical_write_does_not_count_as_a_project_change(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("value = 1\n")
    recorder, tools = _instrumented_tools(project)

    tools["write_file"].handler(path="app.py", content="value = 1\n")

    evidence = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=None,
    )

    assert evidence.events[0].changed is False
    assert evidence.observed_changed_files == ()


def test_reverted_edit_does_not_count_as_a_project_change(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("value = 1\n")
    recorder, tools = _instrumented_tools(project)

    tools["edit_file"].handler(
        path="app.py",
        old_string="value = 1",
        new_string="value = 2",
    )
    tools["edit_file"].handler(
        path="app.py",
        old_string="value = 2",
        new_string="value = 1",
    )

    evidence = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=None,
    )

    assert evidence.observed_changed_files == ()


def test_later_turn_revert_is_compared_with_the_run_baseline(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("value = 1\n")
    baselines = {}

    first = ExecutionRecorder(project, baselines)
    first_tools = {
        tool.name: tool
        for tool in first.instrument(build_tools("Developer", project))
    }
    first_tools["edit_file"].handler(
        path="app.py",
        old_string="value = 1",
        new_string="value = 2",
    )
    assert build_execution_evidence(
        recorder=first,
        status_before=None,
        status_after=None,
    ).observed_changed_files == ("app.py",)

    second = ExecutionRecorder(project, baselines)
    second_tools = {
        tool.name: tool
        for tool in second.instrument(build_tools("Developer", project))
    }
    second_tools["edit_file"].handler(
        path="app.py",
        old_string="value = 2",
        new_string="value = 1",
    )
    second_tools["bash"].handler(command="python3 -m py_compile app.py")

    assert build_execution_evidence(
        recorder=second,
        status_before=None,
        status_after=None,
    ).observed_changed_files == ()


def test_normalizes_paths_and_excludes_runtime_state_from_changes(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / ".agent-state").mkdir()
    (project / ".agent-state" / "handoff.md").write_text("old\n")
    (project / "app.py").write_text("value = 1\n")
    recorder, tools = _instrumented_tools(project)

    tools["edit_file"].handler(
        path=str(project / "app.py"),
        old_string="value = 1",
        new_string="value = 2",
    )
    tools["edit_file"].handler(
        path=".agent-state/handoff.md",
        old_string="old",
        new_string="new",
    )

    evidence = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=" M .agent-state/handoff.md\n",
    )

    assert [event.path for event in evidence.events] == [
        "app.py",
        ".agent-state/handoff.md",
    ]
    assert evidence.current_changed_files == ("app.py",)


def test_failed_validation_kind_is_not_hidden_by_another_success(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("value = 1\n")
    recorder, tools = _instrumented_tools(project)

    tools["edit_file"].handler(
        path="app.py",
        old_string="value = 1",
        new_string="value = 2",
    )
    tools["bash"].handler(command="python3 -c 'assert False'")
    tools["edit_file"].handler(
        path="app.py",
        old_string="value = 2",
        new_string="value = 3",
    )
    tools["bash"].handler(command="python3 -m py_compile app.py")

    failed = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=None,
    )
    assert failed.validation_status == "failed"
    assert failed.unresolved_validation_kinds == ("test",)

    tools["bash"].handler(command="python3 -c 'assert True'")
    recovered = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=None,
    )
    assert recovered.validation_status == "passed"
    assert recovered.successful_validation_kinds == ("syntax", "test")


def test_missing_validation_rewrites_completion_as_rework(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("value = 1\n")
    recorder, tools = _instrumented_tools(project)
    tools["edit_file"].handler(
        path="app.py",
        old_string="value = 1",
        new_string="value = 2",
    )
    evidence = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=None,
    )
    handoff = _handoff()

    assessment = enforce_completion(evidence, handoff)

    assert assessment.outcome == "rework"
    assert assessment.reasons == ("missing_post_change_validation",)
    assert handoff.decision == "rework_required"
    assert handoff.receiver == "Developer"
    assert handoff.files == ["app.py"]


def test_explicit_validation_limitation_allows_limited_handoff(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("value = 1\n")
    recorder, tools = _instrumented_tools(project)
    tools["edit_file"].handler(
        path="app.py",
        old_string="value = 1",
        new_string="value = 2",
    )
    evidence = build_execution_evidence(
        recorder=recorder,
        status_before=None,
        status_after=None,
    )
    handoff = _handoff(
        validation_status="unavailable",
        validation_limitation="The project does not contain a test runner.",
    )

    assessment = assess_completion(evidence, handoff)

    assert assessment.outcome == "limited"
    assert assessment.reasons == ()
