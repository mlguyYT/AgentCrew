"""Host Git reads without repository-configured executable helpers."""

import os
from pathlib import Path
import subprocess


def git_command(
    project: Path,
    *args: str,
    text: bool = True,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    """Run an internal status/diff/ls-files read, capturing output and exit status.

    Arguments are trusted engine options, with untrusted paths following ``--``.
    Safety settings are invocation-local; repository configuration is never edited.
    ``text=False`` returns bytes, for NUL-delimited path inspection.
    """

    if not args or (args[0] not in {"status", "diff", "ls-files"} and args != ("rev-parse", "--show-prefix")):
        raise ValueError("Only status, diff and ls-files Git reads are supported")

    env = {
        key: value for key, value in os.environ.items()
        if not key.upper().startswith("GIT_")
    }
    env.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_SYSTEM=os.devnull,
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_ATTR_NOSYSTEM="1",
        GIT_OPTIONAL_LOCKS="0",
        GIT_TERMINAL_PROMPT="0",
        GIT_NO_LAZY_FETCH="1",
        GIT_ALLOW_PROTOCOL="",
    )
    command = [
        "git", "--no-pager", "-C", str(project),
        "-c", "core.fsmonitor=false",
        "-c", f"core.hooksPath={os.devnull}",
        "-c", f"core.attributesFile={os.devnull}",
        "-c", "diff.external=",
        "-c", "diff.submodule=short",
        "-c", "color.ui=false",
    ]

    # Status/diff can refresh files in submodules, using their local filters.
    # Config and staged-index enumeration invoke no filters; collect overrides
    # first, then inherit them into any subprocess Git starts for submodules.
    root = project.resolve()
    pending = [root]
    visited: set[Path] = set()
    filter_keys: set[str] = set()
    while pending:
        repository = pending.pop()
        if repository in visited:
            continue
        visited.add(repository)
        metadata_command = [*command, "-C", str(repository)]
        filters = subprocess.run(
            [
                *metadata_command, "config", "--null", "--name-only", "--get-regexp",
                r"^filter\..*\.(clean|smudge|process|required)$",
            ],
            env=env, capture_output=True, text=text, check=False,
        )
        if filters.returncode not in {0, 1}:
            return filters
        filter_keys.update(os.fsdecode(filters.stdout).split("\0"))
        if args[0] == "ls-files" or "--no-index" in args:
            continue
        index = subprocess.run(
            [*metadata_command, "ls-files", "--stage", "-z", "--", "."],
            env=env, capture_output=True, text=text, check=False,
        )
        if index.returncode != 0:
            return index
        for record in os.fsdecode(index.stdout).split("\0"):
            if not record.startswith("160000 "):
                continue
            submodule = (repository / record.partition("\t")[2]).resolve()
            if not submodule.is_relative_to(root):
                message = "Git submodule escapes the project root"
                return subprocess.CompletedProcess(
                    command, 128, stdout="" if text else b"",
                    stderr=message if text else message.encode(),
                )
            if (submodule / ".git").exists():
                pending.append(submodule)
    for key in sorted(filter_keys - {""}):
        value = "false" if key.endswith(".required") else ""
        command.extend(["-c", f"{key}={value}"])

    if args[0] == "diff":
        options = list(args)
        boundary = options.index("--") if "--" in options else len(options)
        options[boundary:boundary] = ["--no-ext-diff", "--no-textconv"]
    else:
        options = list(args)
    return subprocess.run(
        [*command, *options],
        env=env, capture_output=True, text=text, check=False,
    )
