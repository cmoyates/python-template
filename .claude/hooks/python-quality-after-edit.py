#!/usr/bin/env python3
"""PostToolUse hook: run Ruff (format + check --fix) and ty on edited Python file."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: str) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, (result.stdout + result.stderr).strip()


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".py") or not Path(file_path).is_file():
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    issues: list[str] = []

    fmt_code, fmt_out = run(["uv", "run", "--quiet", "ruff", "format", file_path], project_dir)
    if fmt_code != 0 and fmt_out:
        issues.append(f"ruff format:\n{fmt_out}")

    lint_code, lint_out = run(
        ["uv", "run", "--quiet", "ruff", "check", "--fix", file_path], project_dir
    )
    if lint_code != 0:
        issues.append(f"ruff check:\n{lint_out}")

    ty_code, ty_out = run(["uv", "run", "--quiet", "ty", "check", file_path], project_dir)
    if ty_code != 0:
        issues.append(f"ty check:\n{ty_out}")

    if issues:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (f"Python quality issues in {file_path}:\n\n" + "\n\n".join(issues)),
                }
            )
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
