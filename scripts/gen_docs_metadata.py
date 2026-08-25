#!/usr/bin/env python3
"""Generate structural JSON indexes for everything under docs/.

Markdown files keep YAML frontmatter as the source of truth for their own
metadata; this script walks the tree, parses it, and emits:

  docs/index.json         — every tracked doc under docs/
  docs/adr/index.json     — type: adr records
  docs/agents/index.json  — everything under docs/agents/, including decision-log.md

Generated artifacts: never hand-edit (see .agents/rules/generated-artifacts.md).
They are tracked in git — regenerate before committing doc changes.

Usage:
  python3 scripts/gen_docs_metadata.py           # write all three indexes
  python3 scripts/gen_docs_metadata.py --check   # exit 1 if output would change
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

INDEX_FILES = {
    DOCS / "index.json": None,
    DOCS / "adr" / "index.json": "adr",
    DOCS / "agents" / "index.json": "agents",
}

DECISION_LOG = DOCS / "agents" / "decision-log.md"
GENERATOR = "scripts/gen_docs_metadata.py"


def parse_frontmatter(text: str, path: Path) -> dict:
    if not text.startswith("---\n"):
        raise SystemExit(f"{path.relative_to(ROOT)}: missing frontmatter block")
    try:
        end = text.index("\n---", 4)
    except ValueError:
        raise SystemExit(f"{path.relative_to(ROOT)}: unterminated frontmatter block")
    meta: dict = {}
    last_list_key: str | None = None
    for raw in text[4:end].splitlines():
        if not raw.strip():
            continue
        if raw.lstrip().startswith("- "):
            if last_list_key is None:
                raise SystemExit(f"{path.relative_to(ROOT)}: list item outside a key: {raw!r}")
            meta[last_list_key].append(raw.lstrip()[2:].strip())
            continue
        if ":" not in raw:
            raise SystemExit(f"{path.relative_to(ROOT)}: unparseable line: {raw!r}")
        key, _, value = raw.partition(":")
        key, value = key.strip(), value.strip()
        if not value:
            meta[key] = []
            last_list_key = key
            continue
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
            last_list_key = None
            continue
        meta[key] = value.strip("'\"")
        last_list_key = None
    return meta


def collect() -> list[dict]:
    records: list[dict] = []
    for path in sorted(DOCS.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        meta = parse_frontmatter(path.read_text(encoding="utf-8"), path)
        records.append(
            {
                "path": rel,
                "id": meta.get("id"),
                "title": meta.get("title"),
                "type": meta.get("type"),
                "status": meta.get("status"),
                "date": meta.get("date"),
                "tags": meta.get("tags", []),
                "related": meta.get("related", []),
            }
        )
    return records


def render(records: list[dict]) -> str:
    payload = {
        "version": 1,
        "generator": GENERATOR,
        "count": len(records),
        "docs": records,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if any index would change")
    args = parser.parse_args()

    records = collect()
    targets: dict[Path, list[dict]] = {
        DOCS / "index.json": records,
        DOCS / "adr" / "index.json": [r for r in records if r["type"] == "adr"],
        DOCS / "agents" / "index.json": [
            r
            for r in records
            if r["type"] != "adr" and Path(r["path"]).parent.name == "agents"
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
        if args.check:
            print(f"drifted  {out_path.relative_to(ROOT)}")
        else:
            out_path.write_text(wanted, encoding="utf-8")
            print(f"wrote    {out_path.relative_to(ROOT)} ({len(subset)} docs)")

    if args.check and drifted:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
