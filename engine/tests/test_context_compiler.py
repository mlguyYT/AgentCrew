import pytest

from agentcrew.agentcrew_root import find_agentcrew_root
from agentcrew.context_compiler import (
    MAX_EXECUTION_CONTEXT_CHARS,
    compile_execution_context,
)
from agentcrew.gates import load_gates_for_role
from agentcrew.routing import Routing


def _routing(
    *,
    recipe: str = "bug-fix",
    skills: list[str] | None = None,
    gates: list[str] | None = None,
) -> Routing:
    return Routing(
        task="Fix the Python API without changing public behavior",
        project="example",
        intent="implementation_or_bug_fix",
        risk="low",
        lane="Fast Lane",
        quality_profile="standard",
        recipe=recipe,
        starting_role="Developer",
        workflow="Developer -> Tester -> Human",
        skills=skills or [],
        gates=gates or [],
    )


def test_compiles_selected_runtime_guidance_under_budget():
    root = find_agentcrew_root()
    routing = _routing(
        skills=["python-pro"],
        gates=["compatibility rollout check", "project constraints check"],
    )
    gate_texts = load_gates_for_role(root, "Developer", routing.gates)

    compiled = compile_execution_context(
        root=root,
        routing=routing,
        role="Developer",
        gate_texts=gate_texts,
    )

    assert len(compiled.text) <= MAX_EXECUTION_CONTEXT_CHARS
    assert compiled.estimated_tokens == (len(compiled.text) + 3) // 4
    assert compiled.fragment_ids == (
        "playbook:developer-execution-loop",
        "gate:compatibility rollout check",
        "gate:project constraints check",
        "recipe:bug-fix",
        "skill:python-pro",
    )
    assert "identify the observable outcome" in compiled.text
    assert "Establish a failing baseline" in compiled.text
    assert "Prefer simple, readable, idiomatic Python" in compiled.text
    assert "Detection triggers" not in compiled.text
    assert "Use This For" not in compiled.text


def test_shares_gate_budget_and_reports_unknown_skills_deterministically():
    root = find_agentcrew_root()
    routing = _routing(skills=["missing-skill"])
    large_gates = [
        (
            f"large gate {gate}",
            "## Runtime Contract\n\n"
            + "\n".join(f"- required check {i}" for i in range(200)),
        )
        for gate in range(8)
    ]

    first = compile_execution_context(
        root=root,
        routing=routing,
        role="Developer",
        gate_texts=large_gates,
    )
    second = compile_execution_context(
        root=root,
        routing=routing,
        role="Developer",
        gate_texts=large_gates,
    )

    assert first == second
    assert len(first.text) <= MAX_EXECUTION_CONTEXT_CHARS
    assert "skill:missing-skill" in first.omitted_fragment_ids
    assert all(
        f"gate:large gate {gate}" in first.fragment_ids
        for gate in range(8)
    )


@pytest.mark.parametrize(
    ("role", "playbook", "expected_text"),
    [
        (
            "Tester",
            "playbook:tester-validation-loop",
            "Developer claim as proof",
        ),
        (
            "Reviewer",
            "playbook:reviewer-inspection-loop",
            "inspect the complete diff",
        ),
    ],
)
def test_compiles_quality_role_runtime_contracts(
    role,
    playbook,
    expected_text,
):
    root = find_agentcrew_root()
    routing = _routing(skills=["python-pro"])
    compiled = compile_execution_context(
        root=root,
        routing=routing,
        role=role,
        gate_texts=[],
    )

    assert len(compiled.text) <= MAX_EXECUTION_CONTEXT_CHARS
    assert compiled.fragment_ids[0] == playbook
    assert expected_text in compiled.text
    assert "skill:python-pro" in compiled.fragment_ids
