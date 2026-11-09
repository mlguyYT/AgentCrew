"""Bounded, read-only Git inspection for Reviewer turns."""

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from .git_safety import git_command


class GitInspectionError(Exception):
    """Raised when repository inspection cannot be completed safely."""


@dataclass(frozen=True)
class GitWorktreeSnapshot:
    """Content-aware state for files currently changed in a Git worktree."""

    entries: tuple[tuple[str, str, str], ...]


def list_git_changed_paths(project_root: Path) -> tuple[str, ...] | None:
    """Return project-scoped changed paths, or None outside a Git worktree."""

    entries = _project_status_entries(project_root)
    return tuple(path for _, path in entries) if entries is not None else None


def capture_git_worktree_snapshot(
    project_root: Path,
) -> GitWorktreeSnapshot | None:
    """Fingerprint currently changed files without persisting their content."""

    records = _project_status_entries(project_root)
    if records is None:
        return None
    entries = tuple(
        (code, path, _path_fingerprint(project_root, path))
        for code, path in records
    )
    return GitWorktreeSnapshot(entries)


def _project_status_entries(project_root: Path) -> tuple[tuple[str, str], ...] | None:
    status = _git_status_z(project_root)
    if status is None:
        return None
    prefix = git_command(project_root, "rev-parse", "--show-prefix")
    if prefix.returncode:
        return None
    relative_prefix = prefix.stdout.rstrip("\n")
    return tuple(
        (code, path[len(relative_prefix):])
        for code, path in _parse_status_z(status)
        if path.startswith(relative_prefix)
    )


def _git_status_z(project_root: Path) -> bytes | None:
    result = git_command(
        project_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--",
        ".",
        text=False,
    )
    return result.stdout if result.returncode == 0 else None


def _parse_status_z(status: bytes) -> tuple[tuple[str, str], ...]:
    records = status.split(b"\0")
    parsed: list[tuple[str, str]] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if len(record) < 4:
            continue
        code = record[:2].decode(errors="replace")
        path = record[3:].decode(errors="replace")
        parsed.append((code, path))
        if "R" in code or "C" in code:
            index += 1
    return tuple(parsed)


def _path_fingerprint(project_root: Path, relative_path: str) -> str:
    path = project_root / relative_path
    try:
        path.relative_to(project_root)
        metadata = path.lstat()
    except (OSError, ValueError):
        return "missing"
    if path.is_symlink():
        try:
            target = os.readlink(path)
        except OSError:
            return "unreadable-symlink"
        return "symlink:" + hashlib.sha256(target.encode()).hexdigest()
    if not path.is_file():
        return f"non-file:{metadata.st_mode}"

    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(64 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return "unreadable-file"
    return "file:" + digest.hexdigest()


def read_git_diff(
    project_root: Path,
    relative_paths: list[str],
    *,
    max_bytes: int = 32_000,
) -> str:
    """Return target-scoped status plus tracked and untracked diffs."""

    path_args = ["--", *(relative_paths or ["."])]
    status = git_command(
        project_root,
        "status",
        "--short",
        "--untracked-files=all",
        *path_args,
    )
    if status.returncode != 0:
        raise GitInspectionError("git status is unavailable for this project")

    diff = git_command(
        project_root,
        "diff",
        "--unified=3",
        "HEAD",
        *path_args,
    )
    tracked_diff = diff.stdout
    if diff.returncode != 0:
        staged = git_command(
            project_root,
            "diff",
            "--cached",
            "--unified=3",
            *path_args,
        )
        unstaged = git_command(
            project_root,
            "diff",
            "--unified=3",
            *path_args,
        )
        if staged.returncode != 0 or unstaged.returncode != 0:
            raise GitInspectionError(
                "git diff is unavailable for this project"
            )
        tracked_diff = staged.stdout + unstaged.stdout

    untracked = git_command(
        project_root,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
        *path_args,
        text=False,
    )
    if untracked.returncode != 0:
        raise GitInspectionError(
            "git untracked-file inspection is unavailable"
        )
    untracked_diffs: list[str] = []
    for raw_path in untracked.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative_path = raw_path.decode(errors="replace")
        new_file_diff = git_command(
            project_root,
            "diff",
            "--no-index",
            "--unified=3",
            "--",
            os.devnull,
            relative_path,
        )
        if new_file_diff.returncode not in {0, 1}:
            raise GitInspectionError(
                "git diff is unavailable for untracked path "
                f"{relative_path!r}"
            )
        if new_file_diff.stdout:
            untracked_diffs.append(new_file_diff.stdout)

    rendered = (
        "--- status ---\n"
        f"{status.stdout or '(clean)'}\n"
        "--- diff ---\n"
        f"{tracked_diff or '(no tracked diff)'}"
        f"{''.join(untracked_diffs)}"
    )
    encoded = rendered.encode()
    if len(encoded) <= max_bytes:
        return rendered
    clipped = encoded[:max_bytes].decode(errors="replace")
    return f"{clipped}\n[TRUNCATED: diff exceeded {max_bytes} bytes]"
