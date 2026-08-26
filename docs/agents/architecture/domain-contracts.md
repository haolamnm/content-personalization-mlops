---
title: "Domain Contracts — Vocabulary and Service Seams"
id: architecture-domain-contracts
date: 2026-08-26
type: contract
status: active
tags: [architecture, contracts, domain-modeling]
related:
  - ./north-star.md
  - ./system-flow.md
  - ../../../CONTEXT-MAP.md
---

# Domain Contracts — Vocabulary and Service Seams

This page answers one question: what does each boundary mean, and what language must not leak across it?

## Core vocabulary

| Term | Meaning | Avoid |
|:---|:---|:---|
| Interaction event | Envelope describing an atomic user action | Database change record |
| Impression | An item was shown | Click or conversion |
| Click | The user engaged with an item | The broader interaction envelope |
| Event time | When the action happened | Processing time |
| Candidate retrieval | Narrowing a large catalog to plausible items | Ranking |
| Ranking | Ordering candidates by predicted relevance | Fetching candidates |
| Online feature | Latest low-latency value for serving | Historical feature value |
| Offline feature | Point-in-time value for training | Current online value |
| Command | Request for a worker or workflow to do something | A fact that already happened |
| Workflow | Durable stateful coordination across steps | A single queued task |

## Boundary contracts

| Boundary | Contract | Owner |
|:---|:---|:---|
| Browser → BFF | OpenAPI feed and interaction APIs | App / BFF |
| Event producers → Kafka | Versioned event envelope, key, topic, and timestamp policy | Event platform |
| Database → Kafka | Debezium connector and CDC envelope policy | CDC |
| Kafka → stream jobs | Topic, partition, key, event-time, and schema policy | Streaming |
| Stream jobs → Iceberg | Table schema, partition, snapshot, and retention policy | Lakehouse |
| Iceberg → Feast | Point-in-time feature-view contract | Feature platform |
| Feast → retrieval | Online lookup, freshness, and missing-value policy | Retrieval |
| Registry → serving | Model artifact, version, compatibility, and promotion policy | ML platform |
| Dispatcher → worker | Task type, idempotency key, retry, timeout, and completion event | Workflow lane |

## Non-negotiable seams

- Retrieval is the only request-time component that directly touches both the online feature store and the candidate index.
- Training reads features through Feast rather than ad-hoc queries against Iceberg.
- Raw event landing preserves what the producer emitted; enrichment and aggregation happen downstream.
- RabbitMQ transports commands; it is not the system of record for recommendation history.
- Cross-language consumers depend on contracts, not shared implementation libraries.

## Edge cases to design explicitly

- An impression without a click is still a training signal and must not disappear.
- A brand-new user needs a cold-start retrieval and ranking policy.
- Late events are assigned by event time and handled according to the stream job’s lateness policy.
- Duplicate commands and duplicate events require idempotency at their owning boundary.
- Missing online features need a defined fallback rather than an accidental null or timeout.

## Read next

- [Messaging](./messaging.md) for event and command semantics.
- [Data platform](./data-platform.md) for schemas, CDC, and storage contracts.
- [Production bar](./production-bar.md) for proof of these invariants.
