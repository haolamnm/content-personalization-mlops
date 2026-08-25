---
description: Never hand-edit generated files (.repos/metadata.json, docs/**/index.json) — fix the generator or curated registry, then regenerate
globs: [".repos/metadata.json", "docs/index.json", "docs/adr/index.json", "docs/agents/index.json"]
alwaysApply: true
---

# Rule: Generated Artifacts

Generated output is never a source of truth and never hand-edited.

## Constraints

- **Edit inputs, not outputs**: provenance facts change in `scripts/repos_registry.json` (curated clone fields) or in each doc's frontmatter (title/status/tags/related); then rerun the matching generator — `gen_repos_metadata.py` or `gen_docs_metadata.py`.
- **Drift check is the gate**: `--check` exiting 1 means either pending regeneration (run it) or hand-edits to revert.
- **New generators follow the pattern**: generator script tracked in `scripts/`, curated inputs tracked, generated output tracked only if public-facing ([ADR 0002](../../docs/adr/0002-local-learning-and-reference-layout.md)).
