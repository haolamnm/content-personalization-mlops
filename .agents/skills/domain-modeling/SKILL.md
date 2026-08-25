---
name: domain-modeling
description: Build, sharpen, and maintain the pipeline's vocabulary and bounded contexts. Use when resolving domain language, editing CONTEXT-MAP.md, or writing module CONTEXT.md files.
---

# Domain Modeling & Ubiquitous Language

Refine the project's vocabulary and bounded-context boundaries during discussions and code changes.

## Bounded Context Hierarchy

- [`CONTEXT-MAP.md`](../../../CONTEXT-MAP.md): top-level graph — Gateway → Kafka → Streaming → Lakehouse → Features → Training → Serving → Retrieval → BFF → App, with Observability and Analytics alongside.
- `platform/<module>/CONTEXT.md` (once each module exists): ubiquitous vocabulary and invariants per context.

## Protocol During Discussions & Implementation

1. **Challenge Fuzzy Terminology**: clarify canonical terms against `CONTEXT-MAP.md`. Recurring traps in this repo:
   - *Impression* (item shown) vs *Click* (engagement) vs *Interaction event* (the envelope containing either) — never interchangeable.
   - *Candidate retrieval* (narrow 10⁶→10²) vs *Ranking* (ordering those candidates by predicted relevance).
   - *Online store* (Redis, latest values, low latency) vs *Offline store* (Iceberg history, point-in-time correct) — a feature lives in both with different contracts.
   - *Event time* (when it happened) vs *Processing time* (when we saw it) — streaming windows run on the former.
2. **Cross-Reference with Working Code**: when behavior is discussed, check whether module seams and tests agree with the stated contract; surface discrepancies immediately.
3. **Probe Edge-Case Scenarios**: stress-test with concrete cases (*"Does an impression without a click still train the ranker?"*, *"What does retrieval return for a brand-new user?"*).
4. **Update Docs Atomically**: when a term or invariant resolves, update `CONTEXT-MAP.md` (or the module `CONTEXT.md`) in the same change — 1-2 sentence definitions, explicit `_Avoid_` aliases.
5. **No Implementation Clutter**: glossaries hold domain vocabulary, not library names, flags, or scratch notes.
