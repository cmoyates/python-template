#!/usr/bin/env python3
"""PostToolUse hook: run Ruff and ty on Python files edited by Codex."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update) File: (.+)$", re.MULTILINE)


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, (result.stdout + result.stderr).strip()


def project_dir_from(payload: dict[str, Any]) -> Path:
    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    code, output = run(["git", "rev-parse", "--show-toplevel"], cwd)
    if code == 0 and output:
        return Path(output.splitlines()[0]).resolve()
    return cwd


def patch_text_from(tool_input: dict[str, Any]) -> str:
    for key in ("patch", "input", "command"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def candidate_files(payload: dict[str, Any], project_dir: Path) -> list[Path]:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return []

    paths: set[Path] = set()

    file_path = tool_input.get("file_path")
    if isinstance(file_path, str):
        paths.add(Path(file_path))

    for raw_path in PATCH_FILE_RE.findall(patch_text_from(tool_input)):
        paths.add(Path(raw_path.strip()))

    python_files: list[Path] = []
    for path in paths:
        resolved = path if path.is_absolute() else project_dir / path
        if resolved.suffix == ".py" and resolved.is_file():
            python_files.append(resolved)

    return sorted(python_files)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    project_dir = project_dir_from(payload)
    files = candidate_files(payload, project_dir)
    if not files:
        sys.exit(0)

    issues: list[str] = []

    for file_path in files:
        display_path = str(file_path.relative_to(project_dir))

        fmt_code, fmt_out = run(
            ["uv", "run", "--quiet", "ruff", "format", str(file_path)], project_dir
        )
        if fmt_code != 0 and fmt_out:
            issues.append(f"ruff format ({display_path}):\n{fmt_out}")

        lint_code, lint_out = run(
            ["uv", "run", "--quiet", "ruff", "check", "--fix", str(file_path)], project_dir
        )
        if lint_code != 0:
            issues.append(f"ruff check ({display_path}):\n{lint_out}")

        ty_code, ty_out = run(["uv", "run", "--quiet", "ty", "check", str(file_path)], project_dir)
        if ty_code != 0:
            issues.append(f"ty check ({display_path}):\n{ty_out}")

    if issues:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Python quality issues after edit:\n\n" + "\n\n".join(issues),
                }
            )
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
