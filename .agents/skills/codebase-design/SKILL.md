---
name: codebase-design
description: Architecture vocabulary and interface design principles. Use when designing pipeline modules, evaluating interface depth, or establishing test seams.
---

# Codebase Design & Module Architecture

Design deep modules with narrow interfaces and rich implementations to maximize caller leverage, maintainer locality, and testability.

## Core Vocabulary

- **Module**: a bounded context's implementation unit (`platform/services/retrieval`, `platform/streaming/…`) hiding complexity behind one contract.
- **Interface**: the public contract a caller must know — API schema, topic + schema version, function signatures, error types.
- **Depth**: capability provided ÷ interface surface. Deep modules do a lot while exposing little.
- **Seam**: a public boundary where behavior is observed without reaching into internals.
- **Adapter**: a concrete implementation at a seam (live Redis client vs fixture-backed fake for tests).
- **Leverage / Locality**: callers learn one simple contract; logic and fixes concentrate in one place.

## Deep vs Shallow Modules

- **Deep (target)**: `recommend(user_id, context) -> RankedFeed` — internally orchestrates candidate retrieval (Rust), feature joins, scoring-model invocation, and impression logging.
- **Shallow (avoid)**: `fetch_candidates()`, `join_features()`, `score()`, `log_impressions()` exposed separately, pushing orchestration onto every caller.

## Architectural Principles

1. **The Deletion Test**: deleting a useless passthrough makes complexity vanish; deleting a deep module scatters it into N callers.
2. **The Interface Is the Test Surface**: tests drive the same seam as production callers.
3. **Seam Discipline**: one adapter is hypothetical; two adapters make a real seam. No trait/factory layers for single implementations — each service stays concrete until a second backend exists.
4. **Designing for Testability**:
   - External effects (clocks, Kafka producers, model registries) enter as parameters, not hardcoded globals.
   - Return typed results; no out-of-band side effects.
   - Minimal surface: fewer public functions, fewer breaking changes.
