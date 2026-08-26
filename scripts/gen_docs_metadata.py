#!/usr/bin/env python3
"""Generate structural JSON indexes for everything under docs/.

Markdown files keep YAML frontmatter as the source of truth for their own
metadata; this script walks the tree, parses it, and emits:

  docs/index.json                    — every tracked doc under docs/
  docs/adr/index.json                — type: adr records
  docs/agents/index.json             — every agent doc under docs/agents/
  docs/agents/architecture/index.json — every architecture doc under its section

Generated artifacts: never hand-edit (see .agents/rules/generated-artifacts.md).
They are tracked in git — regenerate before committing doc changes.

Usage:
  python3 scripts/gen_docs_metadata.py           # write all four indexes
  python3 scripts/gen_docs_metadata.py --check   # exit 1 if output would change
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict, cast

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

GENERATOR = "scripts/gen_docs_metadata.py"


class DocRecord(TypedDict):
    path: str
    id: str
    title: str
    type: str
    status: str
    date: str
    tags: list[str]
    related: list[str]


def parse_frontmatter(text: str, path: Path) -> dict[str, object]:
    if not text.startswith("---\n"):
        raise SystemExit(f"{path.relative_to(ROOT)}: missing frontmatter block")
    try:
        end = text.index("\n---", 4)
    except ValueError:
        raise SystemExit(f"{path.relative_to(ROOT)}: unterminated frontmatter block")
    meta: dict[str, object] = {}
    last_list_key: str | None = None
    for raw in text[4:end].splitlines():
        if not raw.strip():
            continue
        if raw.lstrip().startswith("- "):
            if last_list_key is None:
                raise SystemExit(
                    f"{path.relative_to(ROOT)}: list item outside a key: {raw!r}"
                )
            meta_list = meta.get(last_list_key)
            if not isinstance(meta_list, list):
                raise SystemExit(f"{path.relative_to(ROOT)}: list key holds a value")
            cast("list[str]", meta_list).append(raw.lstrip()[2:].strip())
            continue
        if ":" not in raw:
            raise SystemExit(f"{path.relative_to(ROOT)}: unparseable line: {raw!r}")
        key, _, value = (part.strip() for part in raw.partition(":"))
        if not value:
            meta[key] = []  # type: ignore[assignment]
            last_list_key = key
            continue
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = (
                [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
            )  # type: ignore[assignment]
            last_list_key = None
            continue
        meta[key] = value.strip("'\"")  # type: ignore[assignment]
        last_list_key = None
    return meta


def as_str(meta: dict[str, object], key: str) -> str:
    value = meta.get(key)
    return value if isinstance(value, str) else ""


def as_str_list(meta: dict[str, object], key: str) -> list[str]:
    value = meta.get(key)
    if not isinstance(value, list):
        return []
    strings: list[str] = cast("list[str]", value)
    return list(strings)


def collect() -> list[DocRecord]:
    records: list[DocRecord] = []
    for path in sorted(DOCS.rglob("*.md")):
        meta = parse_frontmatter(path.read_text(encoding="utf-8"), path)
        records.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "id": as_str(meta, "id"),
                "title": as_str(meta, "title"),
                "type": as_str(meta, "type"),
                "status": as_str(meta, "status"),
                "date": as_str(meta, "date"),
                "tags": as_str_list(meta, "tags"),
                "related": as_str_list(meta, "related"),
            }
        )
    return records


def render(records: list[DocRecord]) -> str:
    payload: dict[str, object] = {
        "version": 1,
        "generator": GENERATOR,
        "count": len(records),
        "docs": records,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _as_flag(args: argparse.Namespace, name: str) -> bool:
    value = getattr(args, name, False)
    if not isinstance(value, bool):
        raise SystemExit(f"--{name} must be a boolean flag")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument(
        "--check", action="store_true", help="exit 1 if any index would change"
    )
    args = parser.parse_args()
    check = _as_flag(args, "check")

    records = collect()
    targets: dict[Path, list[DocRecord]] = {
        DOCS / "index.json": records,
        DOCS / "adr" / "index.json": [r for r in records if r.get("type") == "adr"],
        DOCS / "agents" / "index.json": [
            r
            for r in records
            if r.get("type") != "adr" and r["path"].startswith("docs/agents/")
        ],
        DOCS / "agents" / "architecture" / "index.json": [
            r
            for r in records
            if r["path"].startswith("docs/agents/architecture/")
        ],
    }

    drifted = False
    for out_path, subset in targets.items():
        wanted = render(subset)
        current = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        if current == wanted:
            print(f"ok       {out_path.relative_to(ROOT)}")
            continue
        drifted = True
        if check:
            print(f"drifted  {out_path.relative_to(ROOT)}")
        else:
            _ = out_path.write_text(wanted, encoding="utf-8")
            print(f"wrote    {out_path.relative_to(ROOT)} ({len(subset)} docs)")

    if check and drifted:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
