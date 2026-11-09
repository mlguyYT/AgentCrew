"""Run the bundled offline example without modifying the caller's project."""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from .agentcrew_root import AVAILABLE_ROLES, AgentCrewRoot
from .demo_script import demo_provider
from .orchestrator import run
from .routing import classify


BUG_TASK = "Fix broken.py so add_numbers returns a + b"
IDEA_TASK = "I want to add team billing to this app. Help me shape it and implement the first safe version."


def validate_demo_project(project: Path) -> None:
    """Reject unrelated projects before the fixture-specific script runs."""

    project = project.resolve()
    source = project / "broken.py"
    tests = project / "test_broken.py"
    for path in (source, tests):
        if not path.resolve().is_relative_to(project) or not path.is_file():
            raise ValueError(
                "mock-demo requires the bundled broken.py/test_broken.py fixture. "
                "Run 'agentcrew demo' for a fresh isolated example, or choose "
                "a model backend for your project."
            )
    if "return a - b" not in source.read_text():
        raise ValueError(
            "mock-demo expects the original broken.py fixture; it may already "
            "be fixed. Run 'agentcrew demo' for a fresh example."
        )


def run_demo(root: AgentCrewRoot) -> int:
    """Preview two real routes and execute the bug fix with scripted responses."""

    print("AgentCrew offline demo", flush=True)
    print("Scripted model responses; real routing, edits, and tests.", flush=True)
    print("No API key or model service required.\n", flush=True)
    with TemporaryDirectory(prefix="agentcrew-demo-") as directory:
        project = Path(directory)
        fixture = root.path / "engine" / "examples" / "01_python_bug_fix"
        for name in ("broken.py", "test_broken.py"):
            shutil.copyfile(fixture / name, project / name)

        for label, task in (("Tiny bug", BUG_TASK), ("Product idea", IDEA_TASK)):
            routing = classify(root, task=task, project=str(project))
            print(f"{label}: {task}", flush=True)
            print(f"  Lane: {routing.lane}", flush=True)
            print(f"  Workflow: {routing.workflow}", flush=True)
            if routing.has_mid_workflow_human_gate():
                print(
                    "  CEO approval before: "
                    + str(routing.role_after_mid_workflow_human_gate()),
                    flush=True,
                )
            print(flush=True)

        print("Execute the tiny bug fix in a fresh temporary project:", flush=True)
        result = run(
            task=BUG_TASK,
            project_dir=project,
            root=root,
            provider=demo_provider(),
            model_for_role={role: "mock-demo" for role in AVAILABLE_ROLES},
        )
        for handoff in result.handoffs:
            print(f"  {handoff.sender} -> {handoff.receiver}: {handoff.decision}", flush=True)
            for command in handoff.commands:
                print(f"  Validation: {command}", flush=True)
        print(f"  Final decision: {result.final_decision}", flush=True)
        print("  Model API calls: 0", flush=True)
        print("Temporary project removed after the demo.", flush=True)
        return 0 if result.final_decision == "ready_for_human_approval" else 1
