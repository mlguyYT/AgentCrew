from pathlib import Path

from agentcrew.state import build_layout


def test_software_architect_report_path(tmp_path: Path) -> None:
    layout = build_layout(tmp_path)

    assert layout.role_report_path("Software Architect Agent") == (
        tmp_path.resolve() / ".agent-state" / "architecture-report.md"
    )
