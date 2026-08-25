---
description: General Python rules for the ML plane (Feast, Ray, MLflow, FastAPI) — umbrella entry; specifics live in python-*.md siblings
globs: ["**/*.py", "**/pyproject.toml"]
alwaysApply: false
---

# Python General Rules

Python owns the ML plane ([ADR 0004](../../docs/adr/0004-polyglot-language-per-concern.md)): Feast feature definitions, Ray Train/Tune pipelines, MLflow tracking, FastAPI/Ray Serve serving internals. Umbrella entry — read the sibling matching your change:

| Sibling | Covers |
|:---|:---|
| [`python-envs-and-quality.md`](./python-envs-and-quality.md) | uv-only environments, Python 3.14, ty/basedpyright + ruff gates |
| [`python-ml-reproducibility.md`](./python-ml-reproducibility.md) | Seeds, MLflow runs, point-in-time joins, dataset versioning |

## Universal Constraints

- **Python 3.14 via uv only** — never the system interpreter (`.computers/MACBOOK.md` §4 records why).
- **Explicit over clever** at service boundaries: plain functions and dataclasses/pydantic models; no metaclass magic, no import-time side effects.
- **Async only where I/O-bound**: FastAPI/Ray Serve handlers may be async; CPU-bound data work stays sync inside Ray tasks.
- `ruff check` + touched-file type checks pass before delivery ([`verify-before-done`](./verify-before-done.md)).
