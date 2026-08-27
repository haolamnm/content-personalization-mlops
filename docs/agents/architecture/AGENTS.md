---
title: "Architecture Design Index"
id: agents-architecture-map
date: 2026-08-26
type: guide
status: active
tags: [architecture, design]
related:
  - ../AGENTS.md
  - ./index.json
  - ./north-star.md
---

# `docs/agents/architecture/`

Architecture material is intentionally split by question so an agent can load one slice without poisoning its context with the whole platform.

The generated [`index.json`](./index.json) is the routing catalog and frontmatter is the metadata source of truth. Start with [`service-radar.md`](./service-radar.md), then load only the page that owns the question.

## Routing rules

- Product purpose or the “why” → [`north-star.md`](./north-star.md).
- Runtime topology or event/data movement → [`system-flow.md`](./system-flow.md).
- Terms, APIs, events, schemas, or ownership → [`domain-contracts.md`](./domain-contracts.md).
- Reliability, quality, or launch proof → [`production-bar.md`](./production-bar.md).
- Kafka, RabbitMQ, Temporal, or messaging alternatives → [`messaging.md`](./messaging.md).
- PostgreSQL, PgBouncer, CDC, schemas, Iceberg, or query/data tools → [`data-platform.md`](./data-platform.md).
- Feast, Ray, MLflow, orchestration, evaluation, or model serving → [`ml-platform.md`](./ml-platform.md).
- Kubernetes, scaling, identity, secrets, observability, or delivery → [`operations.md`](./operations.md).
- Candidate inventory or “what should we add?” → [`service-radar.md`](./service-radar.md).
- “When does this become an ADR?” → [`decision-gates.md`](./decision-gates.md).

## Document contract

Each page answers one question, declares its scope in frontmatter, separates current facts from target design, and ends with links to adjacent pages instead of repeating them. A page is not a service deployment plan until its decision gate is satisfied.
