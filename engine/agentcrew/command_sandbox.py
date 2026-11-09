"""Filesystem and network isolation for model-issued commands."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


class SandboxUnavailable(RuntimeError):
    """Command execution must stop when OS isolation is unavailable."""


def check_sandbox(project: Path) -> None:
    """Verify isolation before any model is invoked for command-capable roles."""

    command = sandbox_command(project, ["/usr/bin/true"])
    try:
        result = subprocess.run(command, capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SandboxUnavailable("Command isolation could not start; no model execution was started") from exc
    if result.returncode:
        raise SandboxUnavailable(
            "Bubblewrap could not create command isolation. Enable user namespaces "
            "or use the host agent's native execution environment."
        )


def sandbox_command(project: Path, argv: list[str]) -> list[str]:
    """Build a Linux Bubblewrap command with no host-home or network access.

    Runtime executables and libraries are read-only. The project is writable;
    Git and engine-owned state remain read-only. There is no unconfined fallback.
    """

    bubblewrap = shutil.which("bwrap") if sys.platform == "linux" else None
    if bubblewrap is None:
        raise SandboxUnavailable(
            "Isolated engine commands require Bubblewrap (bwrap) on Linux. "
            "Install bubblewrap and enable user namespaces, or use your host "
            "agent's native execution environment. Unconfined execution is disabled."
        )
    project = project.resolve()
    command = [bubblewrap, "--unshare-all", "--die-with-parent", "--new-session", "--cap-drop", "ALL"]
    for directory in ("/usr", "/bin", "/sbin", "/lib", "/lib64"):
        if Path(directory).is_dir():
            command += ["--ro-bind", directory, directory]
    cache = Path("/etc/ld.so.cache")
    if cache.is_file():
        command += ["--ro-bind", str(cache), str(cache)]
    command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]
    command += ["--bind", str(project), str(project)]
    for name in (".git", ".agent-state", ".agentcrew"):
        protected = project / name
        if protected.exists():
            if not protected.resolve().is_relative_to(project):
                raise SandboxUnavailable(f"Protected project path {name} escapes the project root")
            command += ["--ro-bind", str(protected), str(protected)]
    command += ["--chdir", str(project), "--", *argv]
    return command
