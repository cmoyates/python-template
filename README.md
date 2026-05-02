# Python Template

Opinionated starting point for new Python projects. Clone, rename, build.

## What's Included

### Tooling — the Astral suite

- **[uv](https://github.com/astral-sh/uv)** — project and package management
- **[Ruff](https://github.com/astral-sh/ruff)** — formatting, linting, import sorting
- **[ty](https://github.com/astral-sh/ty)** — type checking
- **[pytest](https://github.com/pytest-dev/pytest)** — testing

### Editor (VS Code)

`.vscode/settings.json` configures format-on-save for Python:

- Format with Ruff
- Auto-fix lint issues
- Organize imports
- `ty` resolves imports from the project environment

`.vscode/extensions.json` recommends the Ruff and `ty` extensions.

### AI agents

Pre-wired for **Claude Code** (`.claude/`) and **OpenAI Codex CLI** (`.codex/`). Hooks run Ruff format, lint-fix, and import-sort automatically after the agent edits files, so AI-generated code matches the same standards as save-on-format. A stop hook also runs Ruff, `ty`, and `pytest` over the whole project before the agent finishes — blocking on type errors or failing tests.

Skills live in both `.agents/` and `.claude/` (Claude Code doesn't inherit from `.agents/`), preloaded with:

- **[Matt Pocock's skills](https://github.com/mattpocock/skills)** (snapshot: 2026-05-02) — TDD, diagnose, grill-me, triage, and more. After cloning and renaming the repo, run the `setup-matt-pocock-skills` skill if you plan to use them.
- **[btca-local](https://github.com/davis7dotsh/better-context/blob/main/skills/btca-local/SKILL.md)** — "Better Context App Local". Triggered with `use btca`, it lets the agent search any git repo locally by cloning (or updating) it under `~/.btca/agent/sandbox` and answering questions against the source with citations and code snippets.

## Usage

```bash
uv sync                # install deps
uv run main.py         # run
uv run ruff check      # lint
uv run ruff format     # format
uv run ty check        # typecheck
uv run pytest          # test
```

Tests live under `tests/`; source on the import path lives under `src/`. Markers `unit`, `integration`, and `slow` are pre-registered in `pyproject.toml`.

## Configuration

Lint/format rules live in `pyproject.toml` under `[tool.ruff]`. Defaults:

- Line length: 100
- Target: Python 3.11+
- Lint rules: pycodestyle, Pyflakes, isort, pyupgrade, bugbear, simplify
- Quote style: double
