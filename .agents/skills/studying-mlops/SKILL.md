---
name: studying-mlops
description: Protocol for walking a reference repository end-to-end and producing its study note plus index updates. Use when studying anything under .repos/ (e.g., purchase-prediction-mlops in Phase 0) — reading order, what to extract, where findings land, and the done-when criteria.
---

# Study a Reference Repo

Turn an upstream clone into durable understanding: a topic note in `.notes/`, adopted/rejected patterns logged, and indexes updated. Clones stay untouched ([`reference-clones-read-only`](../../../.agents/rules/reference-clones-read-only.md)).

## Workflow

1. **Provenance first**: confirm the clone is registered (`scripts/repos_registry.json`) and metadata is fresh (`python3 scripts/gen_repos_metadata.py --check`). Register if not.
2. **Read in dependency order**, taking notes as you go:
   - `README.md`, then any docs/ images — what does it claim to be?
   - `Makefile` + every compose file — the real service inventory and wiring.
   - Source top-down per module (for purchase-prediction-mlops: `src/cdc` → `producer` → `streaming` → `feature_stores` → `orchestration` → `ray` → `model_registry` → `serving` → `observability`), then notebooks last.
3. **Write `.notes/topics/<name>.md`** with fixed sections: What it is · Event/data flow in words (source→sink) · Per-module findings (one bullet each, concrete: file names, configs) · **Adopt** list (with why) · **Reject** list (with why) · Open questions for our build.
4. **Update the indexes atomically** ([`keep-docs-alive`](../../../.agents/rules/keep-docs-alive.md)): decision-log row for each adopt/reject worth remembering, roadmap checkbox ticked, `.worklog/FOCUS.md` refreshed.

## Done when

- The topic note answers: "how would I wire this pipeline myself from scratch?" without opening the clone.
- Every Adopt/Reject entry has a one-line rationale tied to our ADRs or constraints (RAM budget, language ownership).
- Roadmap phase checkbox ticked; decision log has the session's rows; FOCUS.md reflects new state.
