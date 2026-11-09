"""Reject aliases and escapes before accessing project runtime state."""

from __future__ import annotations

from pathlib import Path


class UnsafeStatePath(ValueError):
    """Runtime state must not alias another file or project's state."""


def checked_state_path(root: Path, path: Path) -> Path:
    """Validate an explicitly selected state root and a descendant path."""

    root = root.absolute()
    path = path.absolute()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise UnsafeStatePath("State artifact escapes its selected state root") from exc
    if ".." in relative.parts:
        raise UnsafeStatePath("State artifact contains parent traversal")
    current = root
    for part in (None, *relative.parts):
        if part is not None:
            current /= part
        if current.is_symlink():
            raise UnsafeStatePath("Runtime state cannot contain symbolic links")
        if current.is_file() and current.stat().st_nlink > 1:
            raise UnsafeStatePath("Runtime state cannot contain hard-linked artifacts")
    return path


def project_state_path(project: Path, *parts: str) -> Path:
    root = project.resolve() / ".agent-state"
    return checked_state_path(root, root.joinpath(*parts))


def validate_state_tree(root: Path) -> None:
    """Check existing artifacts before a workflow can read or overwrite them."""

    checked_state_path(root, root)
    if root.exists():
        for path in root.rglob("*"):
            checked_state_path(root, path)
