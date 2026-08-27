---
title: "North Star — Content Personalization Platform"
id: architecture-north-star
date: 2026-08-26
type: vision
status: active
tags: [architecture, vision, content-personalization]
related:
  - ./system-flow.md
  - ./domain-contracts.md
  - ./production-bar.md
  - ../../../CONTEXT-MAP.md
---

# North Star — Content Personalization Platform

We are building a production-grade content-personalization platform from zero: a real product experience generates behavioral data, the data becomes trustworthy features, features train recommendation models, and those models improve the next product experience.

The point is not to collect infrastructure. The point is to build one coherent product loop while learning every layer in the place where it earns its complexity.

## The loop

```text
User sees content → impression/click/dwell event → Kafka
       ↑                                      ↓
Personalized feed ← retrieval/ranking ← model ← features ← lakehouse
       ↑                                      ↓
       └──────────── training and evaluation ┘
```

The application creates the events that exercise the data platform, and the data platform creates the recommendations that change the application experience.

## User outcome

The user opens a personalized feed and receives content ranked using identity, recent behavior, content metadata, and request context.

The app records what was shown as an **impression**, what the user engaged with as a **click**, and longer interactions such as **dwell**, **like**, or **share**.

The user sees a fast, useful feed; the platform owns capture, processing, history, features, training, serving, measurement, and recovery behind that experience.

## Architectural posture

- Kafka is the event backbone for durable facts and replayable streams.
- RabbitMQ is an optional command/work queue experiment, not a replacement for Kafka.
- Features have two contracts: historical point-in-time values offline and fresh low-latency values online.
- Candidate retrieval and ranking are separate capabilities.
- Every cross-service boundary is an explicit API, event, schema, or table contract.
- A candidate service must earn its complexity through a capability, a seam, and a proof obligation.

## Current boundary

The documented implemented slice is the Phase 1 data foundation plus the Phase 2 Feature Platform and Content Catalog seams: PostgreSQL, MongoDB, Kafka, MinIO, Debezium CDC, the Go event gateway, the `event-counts` Flink job, the `events-lake` Iceberg sink, Feast/Redis interaction features, and the MongoDB-backed canonical content-item reader.

Training, model serving, retrieval, the BFF, the app, observability, and analytics remain target work; the THINKBOOK k3s data-plane cutover is complete, while production-grade deployment hardening remains target work.

## Read next

- [System flow](./system-flow.md) for the topology and lifecycle.
- [Domain contracts](./domain-contracts.md) for vocabulary and seams.
- [Production bar](./production-bar.md) for what “done” means.
