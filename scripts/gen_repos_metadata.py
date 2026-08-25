#!/usr/bin/env python3
"""Generate .repos/metadata.json — structural provenance for reference clones.

Scans .repos/*/ for git facts (upstream URL, HEAD, branch, commit date) and merges
curated annotations from scripts/repos_registry.json. Generated artifact: never
hand-edit .repos/metadata.json (see .agents/rules/generated-artifacts.md).
Output is timestamp-free by design, so --check is a true idempotence gate.

Usage:
  python3 scripts/gen_repos_metadata.py           # write .repos/metadata.json
  python3 scripts/gen_repos_metadata.py --check   # exit 1 if output would change
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parent.parent
REPOS = ROOT / ".repos"
REGISTRY = ROOT / "scripts" / "repos_registry.json"
OUTPUT = REPOS / "metadata.json"
GENERATOR = "scripts/gen_repos_metadata.py"


class RepoEntry(TypedDict, total=False):
    name: str
    path: str
    upstream: str
    branch: str
    head: dict[str, str]
    added: str | None
    why: str | None
    study_notes: str | None
    pinned: bool


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo), *args), check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def collect(name: str, curated: dict[str, object]) -> RepoEntry:
    repo = REPOS / name
    log_parts = git(repo, "log", "-1", "--format=%s%n%cI").splitlines()
    entry = RepoEntry(
        name=name,
        path=f".repos/{name}",
        upstream=git(repo, "remote", "get-url", "origin"),
        branch=git(repo, "branch", "--show-current"),
        head={
            "sha": git(repo, "rev-parse", "HEAD"),
            "subject": log_parts[0] if log_parts else "",
            "committed_at": log_parts[1] if len(log_parts) > 1 else "",
        },
    )
    optional: dict[str, str | None] = {
        "added": str(curated["added"]) if "added" in curated else None,
        "why": str(curated["why"]) if "why" in curated else None,
        "study_notes": str(curated["study_notes"])
        if "study_notes" in curated
        else None,
    }
    for field in ("added", "why", "study_notes"):
        value = optional[field]
        if value not in (None, ""):
            entry[field] = value
    entry["pinned"] = bool(
        curated.get("pinned", False)
    )  # kept last, matching legacy layout
    return entry


def render(repos: list[RepoEntry]) -> str:
    payload: dict[str, object] = {
        "version": 1,
        "generator": GENERATOR,
        "count": len(repos),
        "repos": repos,
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
        "--check", action="store_true", help="exit 1 if output would change"
    )
    args = parser.parse_args()
    check = _as_flag(args, "check")

    registry: dict[str, dict[str, object]] = (
        json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}
    )

    if not REPOS.exists():
        print(f".repos/ missing at {REPOS}", file=sys.stderr)
        return 2

    names = sorted(p.name for p in REPOS.iterdir() if (p / ".git").is_dir())
    unregistered = [n for n in names if n not in registry]
    if unregistered:
        print(
            f"unregistered clone(s) — add to {REGISTRY.name}: {', '.join(unregistered)}",
            file=sys.stderr,
        )
        return 2
    missing = sorted(k for k in registry if k not in names)
    if missing:
        print(
            f"registered but not on disk — restore clone or drop registry entry: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 2

    wanted = render([collect(n, registry[n]) for n in names])

    if check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != wanted:
            print(f"drifted  {OUTPUT.relative_to(ROOT)}")
            return 1
        print(f"ok       {OUTPUT.relative_to(ROOT)} ({len(names)} repos)")
        return 0

    _ = OUTPUT.write_text(wanted, encoding="utf-8")
    print(f"wrote    {OUTPUT.relative_to(ROOT)} ({len(names)} repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
