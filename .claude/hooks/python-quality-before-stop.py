#!/usr/bin/env python3
"""Stop hook: run Ruff and ty on the whole project; block stop if issues remain."""

from __future__ import annotations

import json
import os
import subprocess
import sys


def run(cmd: list[str], cwd: str) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, (result.stdout + result.stderr).strip()


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}

    if payload.get("stop_hook_active"):
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    issues: list[str] = []

    fmt_code, fmt_out = run(["uv", "run", "--quiet", "ruff", "format", "--check", "."], project_dir)
    if fmt_code != 0:
        issues.append(f"ruff format --check (run `uv run ruff format .` to fix):\n{fmt_out}")

    lint_code, lint_out = run(["uv", "run", "--quiet", "ruff", "check", "."], project_dir)
    if lint_code != 0:
        issues.append(f"ruff check:\n{lint_out}")

    ty_code, ty_out = run(["uv", "run", "--quiet", "ty", "check"], project_dir)
    if ty_code != 0:
        issues.append(f"ty check:\n{ty_out}")

    if issues:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "Python quality issues found before stop. Fix before finishing:\n\n"
                        + "\n\n".join(issues)
                    ),
                }
            )
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
