"""Classify bounded tool calls without retaining arguments or output."""

from __future__ import annotations

import re
import shlex
from pathlib import Path


def classify_tool_call(
    tool_name: str,
    inputs: dict,
    project_root: Path | None,
) -> tuple[str, str | None, str | None, str | None]:
    """Return kind, relative path, command name, and validation kind."""

    if tool_name == "read_file":
        return (
            "inspection",
            _relative_path(inputs.get("path"), project_root),
            None,
            None,
        )
    if tool_name in {"grep", "glob"}:
        return (
            "inspection",
            _relative_path(inputs.get("path"), project_root),
            None,
            None,
        )
    if tool_name == "git_diff":
        paths = inputs.get("paths")
        path = (
            paths[0]
            if isinstance(paths, list)
            and len(paths) == 1
            and isinstance(paths[0], str)
            else "*"
            if not paths
            else None
        )
        return "inspection", path, None, None
    if tool_name in {"write_file", "edit_file"}:
        return (
            "mutation",
            _relative_path(inputs.get("path"), project_root),
            None,
            None,
        )
    if tool_name != "bash":
        return "operation", None, None, None

    command = inputs.get("command")
    if not isinstance(command, str):
        return "operation", None, "unknown", None
    try:
        argv = shlex.split(command)
    except ValueError:
        return "operation", None, "unparseable", None
    if not argv:
        return "operation", None, "empty", None

    binary = Path(argv[0]).name
    args = [arg.casefold() for arg in argv[1:]]
    validation_kind = _validation_kind(binary, args)
    if validation_kind:
        return "validation", None, binary, validation_kind
    if binary in {
        "ls",
        "cat",
        "head",
        "tail",
        "wc",
        "find",
        "grep",
        "rg",
        "echo",
        "pwd",
        "true",
        "false",
    }:
        return "inspection", None, binary, None
    if binary == "black" or (binary == "cargo" and "fmt" in args):
        return "mutation", None, binary, None
    return "operation", None, binary, None


def _validation_kind(binary: str, args: list[str]) -> str | None:
    if binary in {"pytest", "unittest"}:
        return "test"
    if binary in {"ruff", "mypy"}:
        return "lint"
    if binary == "py_compile":
        return "syntax"
    if binary in {"python", "python3"}:
        if "-m" in args:
            module_index = args.index("-m") + 1
            module = args[module_index] if module_index < len(args) else ""
            if module in {"pytest", "unittest"}:
                return "test"
            if module == "py_compile":
                return "syntax"
        if "-c" in args:
            code_index = args.index("-c") + 1
            code = args[code_index] if code_index < len(args) else ""
            if re.search(r"\b(assert|unittest)\b", code):
                return "test"
    if binary == "node":
        if "--test" in args:
            return "test"
        if "--check" in args:
            return "syntax"
    if binary == "npm":
        command = _first_non_option(args)
        if command == "audit":
            return "audit"
        if command == "test":
            return "test"
        if command == "run":
            index = args.index(command) + 1
            if index < len(args):
                return _script_validation_kind(args[index])
    if binary == "npx":
        command = _first_non_option(args)
        return _script_validation_kind(command) if command else None
    if binary == "cargo":
        return {
            "test": "test",
            "check": "build",
            "build": "build",
            "clippy": "lint",
            "audit": "audit",
        }.get(_first_non_option(args))
    if binary == "go":
        return {
            "test": "test",
            "vet": "lint",
            "build": "build",
        }.get(_first_non_option(args))
    if binary == "make":
        command = _first_non_option(args)
        return _script_validation_kind(command) if command else None
    if binary == "black" and "--check" in args:
        return "lint"
    return None


def _first_non_option(args: list[str]) -> str | None:
    return next((arg for arg in args if not arg.startswith("-")), None)


def _script_validation_kind(name: str) -> str | None:
    tokens = set(re.findall(r"[a-z0-9]+", name.casefold()))
    if tokens & {"test", "tests", "spec", "specs", "jest", "vitest"}:
        return "test"
    if tokens & {"lint", "clippy", "eslint"}:
        return "lint"
    if tokens & {"check", "typecheck", "build", "tsc"}:
        return "build"
    if "audit" in tokens:
        return "audit"
    return None


def _relative_path(value: object, project_root: Path | None) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if project_root is None:
        return None if path.is_absolute() else path.as_posix()
    try:
        return (project_root / path).resolve().relative_to(project_root).as_posix()
    except ValueError:
        return None
