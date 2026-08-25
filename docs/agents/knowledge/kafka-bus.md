---
title: "Kafka Bus"
id: agents-knowledge-kafka-bus
date: 2026-08-25
type: knowledge
status: active
tags: [kafka, listeners, topics, envelopes]
related:
  - ../knowledge/image-pins.md
  - ../../../platform/services/event-gateway/CONTEXT.md
---

# Kafka Bus

## Listener scheme (never regress this)

Two roles, two listeners — sharing one port between roles breaks cross-container clients via metadata redirects:

- **In-mesh clients**: `kafka:9092` (advertised as `kafka:29092`)
- **Host-only clients**: binds `127.0.0.1:29094`, advertised as `localhost:29094`

Host-run dev default for apps: `KAFKA_BOOTSTRAP_SERVERS=localhost:29094`; containers on `mlops-data` use `kafka:9092`.

## Topics

- Kafka 4.x has **auto-create disabled** → topics are created explicitly by `make topics-ensure` before any producer/consumer starts. A downed data group fails fast there instead of crash-looping clients.
- Current topic: `mlops.events.raw`, 3 partitions, keyed by `user_id` so per-user ordering survives partitioning.

## Envelope contract

Gateway-produced interaction events: `{user_id, item_id, event_type, created_at}` — server-stamped RFC-3339 UTC at the edge; IDs trimmed pre-produce so keying holds; vocabulary is impression/click/dwell/like/share. Downstream consumers parse defensively (unknown fields ignored, poison records skipped) but the contract lives in the gateway's CONTEXT.md.
