---
title: "Event Counts Job Context"
id: event-counts-context
date: 2026-08-25
type: context
status: active
tags: [java, flink, streaming]
related:
  - ../../../CONTEXT-MAP.md
  - ../../../.agents/rules/java-general.md
---

# Event Counts (`platform/streaming/event-counts/`)

First Java stream job ([ADR 0004](../../../docs/adr/0004-polyglot-language-per-concern.md): Java owns stream processing). Consumes **`mlops.events.raw`** (group `mlops-flink-event-counts`), parses gateway envelopes, counts per `event_type` in 10s event-time tumbling windows keyed by type. Late data beyond watermark+5s goes to a side output — silent drops are banned.

## Shape

- `RawEvent` — immutable record + event-type vocabulary check
- `EventParser` — Jackson wire mapping, malformed input yields empty (never crashes the job)
- `EventCountsJob` — wiring: KafkaSource → parse → watermarks → window aggregate; pipeline factored for MiniCluster injection

## Config

| Env | Default | Meaning |
|:---|:---|:---|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:29094` | host-run dev default; mesh uses `kafka:9092` |

## Boundaries

- Reads the raw topic only — this job proves consumption + windowing; enrichment/aggregation semantics land with later jobs, lakehouse sink lands with the Iceberg slice.
- Runs embedded (`LocalStreamEnvironment`) until a deployment-shape ADR exists; checkpoint storage is dev-local (AGENTS.md documents all resilience knobs).
- Upstream contract: gateway envelope `{user_id, item_id, event_type, created_at}` with server-stamped RFC-3339 UTC time.

## Verification

`mvn -q package` + `mvn -q test` — 10 active tests (7 parser incl. null-`created_at` poison case, 3 deterministic MiniCluster pipeline tests for per-type counts across windows, too-late side output, malformed filtering) using punctuated watermarks and Sink V2 collectors; one disabled repro documents the embedded parallelism>1 constraint (AGENTS.md). Runs embedded at parallelism 1; e2e-verified against real Kafka on THINKBOOK.
