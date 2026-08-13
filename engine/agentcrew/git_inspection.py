"""Bounded, read-only Git inspection for Reviewer turns."""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitInspectionError(Exception):
    """Raised when repository inspection cannot be completed safely."""


@dataclass(frozen=True)
class GitWorktreeSnapshot:
    """Content-aware state for files currently changed in a Git worktree."""

    entries: tuple[tuple[str, str, str], ...]


def list_git_changed_paths(project_root: Path) -> tuple[str, ...] | None:
    """Return project-scoped changed paths, or None outside a Git worktree."""

    status = _git_status_z(project_root)
    if status is None:
        return None
    return tuple(path for _, path in _parse_status_z(status))


def capture_git_worktree_snapshot(
    project_root: Path,
) -> GitWorktreeSnapshot | None:
    """Fingerprint currently changed files without persisting their content."""

    status = _git_status_z(project_root)
    if status is None:
        return None
    entries = tuple(
        (code, path, _path_fingerprint(project_root, path))
        for code, path in _parse_status_z(status)
    )
    return GitWorktreeSnapshot(entries)


def _git_status_z(project_root: Path) -> bytes | None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--",
            ".",
        ],
        capture_output=True,
        check=False,
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
    status = subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "status",
            "--short",
            "--untracked-files=all",
            *path_args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode != 0:
        raise GitInspectionError("git status is unavailable for this project")

    diff_args = [
        "git",
        "-C",
        str(project_root),
        "diff",
        "--no-ext-diff",
        "--unified=3",
        "HEAD",
        *path_args,
    ]
    diff = subprocess.run(
        diff_args,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked_diff = diff.stdout
    if diff.returncode != 0:
        staged = subprocess.run(
            [
                "git",
                "-C",
                str(project_root),
                "diff",
                "--cached",
                "--no-ext-diff",
                "--unified=3",
                *path_args,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        unstaged = subprocess.run(
            [
                "git",
                "-C",
                str(project_root),
                "diff",
                "--no-ext-diff",
                "--unified=3",
                *path_args,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if staged.returncode != 0 or unstaged.returncode != 0:
            raise GitInspectionError(
                "git diff is unavailable for this project"
            )
        tracked_diff = staged.stdout + unstaged.stdout

    untracked = subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            *path_args,
        ],
        capture_output=True,
        check=False,
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
        new_file_diff = subprocess.run(
            [
                "git",
                "diff",
                "--no-index",
                "--no-ext-diff",
                "--unified=3",
                "--",
                os.devnull,
                relative_path,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
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
