"""Gate playbook loading (#2)."""

from agentcrew.gates import load_gates_for_role, render_gate_section
from agentcrew.agentcrew_root import find_agentcrew_root


def test_developer_gets_dependency_supply_chain_gate():
    root = find_agentcrew_root()
    loaded = load_gates_for_role(root, "Developer", ["dependency and supply-chain gate"])
    assert len(loaded) == 1
    gate, text = loaded[0]
    assert gate == "dependency and supply-chain gate"
    # The actual methodology playbook content
    assert "supply" in text.lower() or "dependency" in text.lower()


def test_tester_gets_validation_gates():
    root = find_agentcrew_root()
    loaded = load_gates_for_role(root, "Tester", ["tester validation", "full validation"])
    # Both map to testing.md but we dedupe — actually no, we load each gate
    # separately. The orchestrator wouldn't see duplicates because the
    # classifier shouldn't emit both. Either way, just confirm Tester gets them.
    assert {g for g, _ in loaded} == {"tester validation", "full validation"}


def test_developer_does_not_get_release_gate():
    """release report belongs to Release Manager, not Developer."""
    root = find_agentcrew_root()
    loaded = load_gates_for_role(root, "Developer", ["release report"])
    assert loaded == []


def test_release_manager_gets_release_gate():
    root = find_agentcrew_root()
    loaded = load_gates_for_role(root, "Release Manager", ["release report"])
    assert len(loaded) == 1


def test_unknown_gate_silently_ignored():
    root = find_agentcrew_root()
    loaded = load_gates_for_role(root, "Developer", ["some made-up gate name"])
    assert loaded == []


def test_render_gate_section_empty_when_no_gates():
    assert render_gate_section([]) == ""


def test_render_gate_section_includes_each_gate():
    section = render_gate_section([("alpha", "alpha body"), ("beta", "beta body")])
    assert "## Triggered gates for your role" in section
    assert "### Gate: `alpha`" in section
    assert "alpha body" in section
    assert "### Gate: `beta`" in section
    assert "beta body" in section


def test_all_gate_mappings_resolve():
    """Every gate string in _GATE_FILES must resolve to an actual methodology file."""
    from agentcrew.gates import _GATE_FILES

    root = find_agentcrew_root()
    missing = []
    for gate, relpath in _GATE_FILES.items():
        try:
            root.methodology_file(relpath)
        except FileNotFoundError:
            missing.append((gate, relpath))
    assert missing == [], f"Gate playbooks reference methodology files that don't exist: {missing}"
