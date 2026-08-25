---
description: Environments and code quality for the Python ML plane — uv-only venvs, typing, lint gates
globs: ["**/*.py", "**/pyproject.toml"]
alwaysApply: false
---

# Rule: Python Environments & Quality

## Constraints

- **uv owns every environment**: `uv venv` + `uv pip`/`uv sync` per service; the system interpreter (3.9.6, see `.computers/MACBOOK.md`) is never used; `uv.lock` is committed per project.
- **Python 3.14** is the target (`requires-python = ">=3.14"`); stdlib-deprecation warnings are treated as defects, not noise.
- **Type hints everywhere**; checked by **basedpyright** (strict mode) plus **ty** on touched files — part of [`verify-before-done`](./verify-before-done.md).
- **ruff** owns linting AND formatting; type checking is **ty + basedpyright**. No mypy, no black, no flake8/isort — one modern Astral-first stack, nothing traditional.
- Notebooks are for exploration only: anything a phase depends on graduates into an importable module with tests; notebook outputs are stripped before any commit.
- No `pip install` outside uv, no `--break-system-packages`, ever.
