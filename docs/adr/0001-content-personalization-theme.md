---
title: "ADR 0001 — Content Personalization as the Carrying Theme"
id: adr-0001
date: 2026-08-24
type: adr
status: accepted
tags: [mlops, theme, positioning]
related:
  - ../agents/decision-log.md
  - ./0004-polyglot-language-per-concern.md
---

# ADR 0001 — Content Personalization as the Carrying Theme

## Status

Accepted (2026-08-24; content personalization chosen between two candidate themes).

## Context

The workspace needs one product theme carried through every MLOps phase, so each service is learned in a real role instead of in isolation. Candidates: IoT prediction vs content personalization.

## Decision

**Content personalization.** User interactions flow CDC → Kafka → stream jobs → lakehouse → features → training → serving → app, and the app emits new interactions — a closed loop that exercises ingestion, streaming, features, training, serving, observability and BI against one coherent domain.

## Alternatives Considered

1. **IoT prediction (sensor telemetry)**: rejected — telemetry pipelines are mostly append-only; weaker natural loop back into the product, less variety in event semantics.
2. **No theme (per-phase toy demos)**: rejected — disconnected demos do not compound into a portfolio-grade system.

## Consequences

- Event semantics (impression/click/dwell/like) become the ubiquitous language; see CONTEXT-MAP §3.
- A recommendation UI eventually closes the data loop, making Phase 5+ self-testing.
- Catalog/metadata naturally pulls MongoDB in alongside Postgres; retrieval naturally pulls Elasticsearch.
