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

ROOT = Path(__file__).resolve().parent.parent
REPOS = ROOT / ".repos"
REGISTRY = ROOT / "scripts" / "repos_registry.json"
OUTPUT = REPOS / "metadata.json"
GENERATOR = "scripts/gen_repos_metadata.py"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo), *args), check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def collect(name: str, curated: dict) -> dict:
    repo = REPOS / name
    log_parts = git(repo, "log", "-1", "--format=%s%n%cI").splitlines()
    subject = log_parts[0] if log_parts else ""
    committed_at = log_parts[1] if len(log_parts) > 1 else ""
    entry = {
        "name": name,
        "path": f".repos/{name}",
        "upstream": git(repo, "remote", "get-url", "origin"),
        "branch": git(repo, "branch", "--show-current"),
        "head": {
            "sha": git(repo, "rev-parse", "HEAD"),
            "subject": subject,
            "committed_at": committed_at,
        },
        "added": curated.get("added"),
        "why": curated.get("why"),
        "study_notes": curated.get("study_notes"),
        "pinned": curated.get("pinned", False),
    }
    return {k: v for k, v in entry.items() if v not in (None, "")}


def render(repos: list[dict]) -> str:
    payload = {
        "version": 1,
        "generator": GENERATOR,
        "count": len(repos),
        "repos": repos,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if output would change")
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}

    if not REPOS.exists():
        print(f".repos/ missing at {REPOS}", file=sys.stderr)
        return 2

    names = sorted(p.name for p in REPOS.iterdir() if (p / ".git").is_dir())
    unregistered = [n for n in names if n not in registry]
    if unregistered:
        print(f"unregistered clone(s) — add to {REGISTRY.name}: {', '.join(unregistered)}", file=sys.stderr)
        return 2
    missing = sorted(k for k in registry if k not in names)
    if missing:
        print(f"registered but not on disk — restore clone or drop registry entry: {', '.join(missing)}", file=sys.stderr)
        return 2

    wanted = render([collect(n, registry[n]) for n in names])

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != wanted:
            print(f"drifted  {OUTPUT.relative_to(ROOT)}")
            return 1
        print(f"ok       {OUTPUT.relative_to(ROOT)} ({len(names)} repos)")
        return 0

    OUTPUT.write_text(wanted, encoding="utf-8")
    print(f"wrote    {OUTPUT.relative_to(ROOT)} ({len(names)} repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
