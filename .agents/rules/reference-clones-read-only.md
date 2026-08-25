---
description: .repos/ clones are untouched upstream checkouts; learning goes to .notes/, provenance to the registry
globs: [".repos/**"]
alwaysApply: true
---

# Rule: Reference Clones Read Only

`.repos/` holds third-party code for study, never a fork base.

## Constraints

- **No edits inside clones**: no fixes, formatting, experiments, or branch commits in upstream checkouts; observations go to `.notes/topics/<name>.md` ([studying-mlops](../skills/studying-mlops/SKILL.md) protocol).
- **Register on clone**: every new clone gets a `scripts/repos_registry.json` entry (upstream, added date, why) and `python3 scripts/gen_repos_metadata.py` re-run.
- **Pin deliberately**: clones track upstream default branches unless a study needs a pinned tag; pins recorded in the registry.
- **Never stage**: `.repos/` is gitignored by design ([ADR 0002](../../docs/adr/0002-local-learning-and-reference-layout.md)).
