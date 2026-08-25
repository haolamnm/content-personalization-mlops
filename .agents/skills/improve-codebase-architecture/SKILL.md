---
name: improve-codebase-architecture
description: Scan the codebase for architectural friction, shallow abstractions, or test fragility, and propose actionable deepening refactors.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** that turn shallow modules into deep, resilient abstractions.

## Process

### 1. Identify Friction Hotspots
- **User Directed**: start where the user points, if they point.
- **Git Churn**: `git log --oneline -n 30` — prioritize files under active evolution.
- **Domain Context**: consult [`CONTEXT-MAP.md`](../../../CONTEXT-MAP.md) for intended boundaries before proposing moves.

### 2. Diagnose Module Depth
Pipeline-flavored smells:
- **Leaky stages**: an entrypoint orchestrating retrieval/scoring logic inline instead of delegating to the owning module with one call.
- **Shallow helpers**: pass-through functions adding no invariant, validation, or simplification.
- **Cross-context coupling**: one bounded context reading another's internals (e.g., BFF querying Redis directly — CONTEXT-MAP §2 reserves that for Retrieval alone).
- **Test fragility**: tests asserting private outputs instead of behavior through public seams (`tdd` seam principle).
- **Config creep**: flags threaded through five layers as loose parameters instead of one typed config struct.

### 3. Propose Deepening Plan
For each finding:
1. Current shallow interface + concrete caller pain points.
2. Proposed deep interface — fewer parameters, clear types, encapsulated effects.
3. How caller complexity drops and testability rises.
4. A step-by-step migration preserving behavior; no breaking working callers mid-step.

Proposals respect `.agents/rules/minimal-footprint.md`: deepening is justified by demonstrated friction, not aesthetics.
