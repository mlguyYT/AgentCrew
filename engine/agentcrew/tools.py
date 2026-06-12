"""Bounded local tools — the load-bearing safety surface.

Each role gets a curated subset of these. Tools run on the operator's
filesystem (the project directory passed to the orchestrator); they are
not provider-hosted. Every tool refuses to escape the project root, and
the bash tool enforces a command allowlist plus a denylist of destructive
patterns.

Roles cannot override their allowlist — the orchestrator passes only the
tool definitions the agent is allowed to call, and the API rejects any
tool_use whose name isn't in that list.
"""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class ToolError(Exception):
    """Raised inside a tool implementation. The orchestrator turns this into
    a tool_result with is_error=True so the model can recover."""

    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class ToolSpec:
    """A single tool: its provider-facing JSON schema plus the callable that runs it."""

    name: str
    description: str
    input_schema: dict
    handler: Callable[..., str]


# --- Sandbox helpers ----------------------------------------------------------


def _resolve(project_root: Path, relpath: str) -> Path:
    """Resolve `relpath` strictly under `project_root`. Reject escapes."""
    if not isinstance(relpath, str) or not relpath:
        raise ToolError("path must be a non-empty string")
    candidate = (project_root / relpath).resolve()
    root = project_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ToolError(f"path {relpath!r} escapes the project root")
    return candidate


# --- Bash safety --------------------------------------------------------------

# Commands the Developer is allowed to invoke. We allowlist by argv[0] only —
# arguments are user-controllable but the binary is not.
_DEVELOPER_BASH_ALLOWLIST = {
    "ls", "cat", "head", "tail", "wc", "find", "grep", "rg",
    "python", "python3", "py_compile",
    "node", "npm", "npx",
    "go", "cargo", "rustc",
    "pytest", "unittest",
    "ruff", "mypy", "black",
    "make", "echo", "pwd", "true", "false",
}

# Commands the Tester is allowed to invoke. Tester commands are validation
# commands only; the orchestrator also checks that Tester does not mutate a git
# worktree during the role turn.
_TESTER_BASH_ALLOWLIST = {
    "ls", "cat", "head", "tail", "wc", "find", "grep", "rg",
    "pytest", "unittest",
    "node", "npm",
    "go", "cargo",
    "echo", "pwd", "true", "false",
}

# Denylisted patterns anywhere in the command. Regex applied to the whole string.
_BASH_DENY_PATTERNS = [
    re.compile(r"\brm\s+-rf\b"),
    re.compile(r"\bgit\s+(push|reset\s+--hard|clean\s+-fd|checkout\s+--)"),
    re.compile(r"\bcurl\b"),
    re.compile(r"\bwget\b"),
    re.compile(r"\bpip\s+install\b"),
    re.compile(r"\bnpm\s+install\b"),
    re.compile(r"\bsudo\b"),
    re.compile(r">\s*/dev/sda"),
    re.compile(r"\bmkfs\b"),
    re.compile(r"\bdd\s+if="),
    re.compile(r"\b:\s*\(\s*\)\s*\{"),  # fork bomb
]


def _bash_check(command: str, allowlist: set[str]) -> list[str]:
    if not command or not command.strip():
        raise ToolError("command must be non-empty")
    for pat in _BASH_DENY_PATTERNS:
        if pat.search(command):
            raise ToolError(
                f"command blocked by denylist (matched {pat.pattern!r})"
            )
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        raise ToolError(f"command failed to parse: {exc}") from exc
    if not argv:
        raise ToolError("command parsed to empty argv")
    binary = Path(argv[0]).name  # strip any path prefix
    if binary not in allowlist:
        raise ToolError(
            f"command {binary!r} not in this role's allowlist; "
            f"allowed: {sorted(allowlist)}"
        )
    return argv


# --- Tool implementations -----------------------------------------------------


def _read_file(project_root: Path, path: str, max_bytes: int = 64_000) -> str:
    p = _resolve(project_root, path)
    if not p.exists():
        raise ToolError(f"file not found: {path}")
    if not p.is_file():
        raise ToolError(f"not a file: {path}")
    data = p.read_bytes()
    if len(data) > max_bytes:
        truncated = data[:max_bytes].decode("utf-8", errors="replace")
        return f"{truncated}\n\n[TRUNCATED: file is {len(data)} bytes; first {max_bytes} shown]"
    return data.decode("utf-8", errors="replace")


def _write_file(project_root: Path, path: str, content: str) -> str:
    p = _resolve(project_root, path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {len(content)} bytes to {path}"


def _edit_file(project_root: Path, path: str, old_string: str, new_string: str) -> str:
    p = _resolve(project_root, path)
    if not p.exists():
        raise ToolError(f"file not found: {path}")
    original = p.read_text()
    occurrences = original.count(old_string)
    if occurrences == 0:
        raise ToolError(f"old_string not found in {path}")
    if occurrences > 1:
        raise ToolError(
            f"old_string matches {occurrences} times in {path}; "
            f"provide more surrounding context to make it unique"
        )
    p.write_text(original.replace(old_string, new_string, 1))
    return f"edited {path} (1 replacement)"


def _bash(project_root: Path, allowlist: set[str], command: str, timeout: int = 30) -> str:
    argv = _bash_check(command, allowlist)
    try:
        result = subprocess.run(
            argv,
            shell=False,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(project_root)},
        )
    except subprocess.TimeoutExpired:
        raise ToolError(f"command timed out after {timeout}s")
    out = (result.stdout or "")[:8000]
    err = (result.stderr or "")[:4000]
    return (
        f"exit={result.returncode}\n"
        f"--- stdout ---\n{out}\n"
        f"--- stderr ---\n{err}"
    )


def _grep(project_root: Path, pattern: str, path: str = ".", max_results: int = 50) -> str:
    p = _resolve(project_root, path)
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        raise ToolError(f"invalid regex: {exc}") from exc
    matches: list[str] = []
    files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
    for f in files:
        try:
            for i, line in enumerate(f.read_text().splitlines(), start=1):
                if rx.search(line):
                    rel = f.relative_to(project_root)
                    matches.append(f"{rel}:{i}: {line[:200]}")
                    if len(matches) >= max_results:
                        return "\n".join(matches) + f"\n[TRUNCATED at {max_results}]"
        except (UnicodeDecodeError, PermissionError):
            continue
    return "\n".join(matches) if matches else "(no matches)"


def _glob(project_root: Path, pattern: str, max_results: int = 100) -> str:
    matches = []
    for p in project_root.rglob(pattern):
        if p.is_file():
            try:
                matches.append(str(p.relative_to(project_root)))
            except ValueError:
                continue
        if len(matches) >= max_results:
            break
    return "\n".join(matches) if matches else "(no matches)"


# --- Tool specs (per role allowlist) ------------------------------------------


def build_tools(role: str, project_root: Path) -> list[ToolSpec]:
    """Return the bounded tool set this role is allowed to use."""

    read_spec = ToolSpec(
        name="read_file",
        description="Read a UTF-8 text file from the project. Path must be relative to the project root.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relative to project root"},
            },
            "required": ["path"],
        },
        handler=lambda path: _read_file(project_root, path),
    )

    write_spec = ToolSpec(
        name="write_file",
        description="Create or overwrite a file. Path must be relative to the project root.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
        handler=lambda path, content: _write_file(project_root, path, content),
    )

    edit_spec = ToolSpec(
        name="edit_file",
        description=(
            "Replace one exact occurrence of old_string with new_string in a file. "
            "Fails if old_string is not found or appears multiple times."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
            },
            "required": ["path", "old_string", "new_string"],
        },
        handler=lambda path, old_string, new_string: _edit_file(
            project_root, path, old_string, new_string
        ),
    )

    grep_spec = ToolSpec(
        name="grep",
        description="Search file contents for a regex. Returns up to 50 matches.",
        input_schema={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Python regex"},
                "path": {"type": "string", "description": "File or directory; default '.'", "default": "."},
            },
            "required": ["pattern"],
        },
        handler=lambda pattern, path=".": _grep(project_root, pattern, path),
    )

    glob_spec = ToolSpec(
        name="glob",
        description="Find files by glob pattern. Returns up to 100 paths.",
        input_schema={
            "type": "object",
            "properties": {"pattern": {"type": "string", "description": "e.g. '**/*.py'"}},
            "required": ["pattern"],
        },
        handler=lambda pattern: _glob(project_root, pattern),
    )

    dev_bash = ToolSpec(
        name="bash",
        description=(
            "Run a shell command in the project root. Network access denied. "
            "Destructive operations denied. 30-second timeout."
        ),
        input_schema={
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
        handler=lambda command: _bash(project_root, _DEVELOPER_BASH_ALLOWLIST, command),
    )

    test_bash = ToolSpec(
        name="bash",
        description=(
            "Run a read-only shell command (tests, linters, file listing). "
            "Source files cannot be modified."
        ),
        input_schema={
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
        handler=lambda command: _bash(project_root, _TESTER_BASH_ALLOWLIST, command),
    )

    # Documentation can write to docs paths only. We enforce this by
    # wrapping write_file/edit_file with a path-prefix guard.
    def _doc_write(path: str, content: str) -> str:
        _check_doc_path(path)
        return _write_file(project_root, path, content)

    def _doc_edit(path: str, old_string: str, new_string: str) -> str:
        _check_doc_path(path)
        return _edit_file(project_root, path, old_string, new_string)

    doc_write_spec = ToolSpec(
        name="write_file",
        description="Create or overwrite a documentation file (Markdown / docs/ / README* / CHANGELOG*).",
        input_schema=write_spec.input_schema,
        handler=_doc_write,
    )
    doc_edit_spec = ToolSpec(
        name="edit_file",
        description=edit_spec.description + " Restricted to documentation files for this role.",
        input_schema=edit_spec.input_schema,
        handler=_doc_edit,
    )

    # Role names below match agent-team/agents/*.md exactly.
    # Same allowlist shape; just keyed on the methodology's vocabulary.
    if role == "Developer":
        return [read_spec, write_spec, edit_spec, dev_bash]
    if role == "Tester":
        return [read_spec, test_bash]
    if role == "Reviewer":
        return [read_spec, grep_spec, glob_spec]
    if role == "Researcher Agent":
        return [read_spec, grep_spec, glob_spec]
    if role == "Security Reviewer":
        return [read_spec, grep_spec, glob_spec]
    if role == "UX / Design Reviewer":
        return [read_spec, grep_spec, glob_spec]
    if role == "Documentation Agent":
        return [read_spec, grep_spec, glob_spec, doc_write_spec, doc_edit_spec]
    if role == "Support Triage Agent":
        return [read_spec, grep_spec, glob_spec]
    if role == "Release Manager":
        return [read_spec, grep_spec, glob_spec]
    if role == "LLM Agent":
        return [read_spec, grep_spec, glob_spec]
    if role == "CNN Agent":
        return [read_spec, grep_spec, glob_spec]
    if role == "Skill Validator":
        return [read_spec, grep_spec, glob_spec]
    if role in ("Advisor", "Idea Consultant", "Product Manager"):
        # Advisory/planning roles are read-only by default — they produce
        # plans/decisions, not source changes.
        return [read_spec, grep_spec, glob_spec]
    raise ValueError(f"unknown role: {role!r}")


# Documentation role can only write files whose path matches one of these.
_DOC_PATH_PATTERNS = re.compile(
    r"(?i)(^|/)(README|CHANGELOG|CONTRIBUTING|SECURITY|AUTHORS|NOTICE)([._-]|$)"
    r"|\.md$|\.markdown$|\.rst$|\.txt$"
    r"|(^|/)docs?(/|$)"
)


def _check_doc_path(path: str) -> None:
    if not _DOC_PATH_PATTERNS.search(path):
        raise ToolError(
            f"Documentation role may only write to docs, README*, CHANGELOG*, "
            f"or *.md/.rst/.txt files; got {path!r}"
        )
