---
title: "Events Lake Context"
id: events-lake-context
date: 2026-08-26
type: context
status: active
tags: [java, flink, iceberg, lakehouse]
related:
  - ../../../CONTEXT-MAP.md
  - ../../../docs/adr/0008-iceberg-lake-sink-dual-pin.md
  - ../../../.agents/rules/java-general.md
---

# Events Lake (`platform/streaming/events-lake/`)

Second Java stream job. Consumes **`mlops.events.raw`** (group `mlops-flink-events-lake`) and appends valid envelopes to the Iceberg table **`mlops_lake.events_raw`** (Parquet on MinIO, JDBC catalog state in our Postgres). First ACID lakehouse surface of the platform — [ADR 0008](../../../docs/adr/0008-iceberg-lake-sink-dual-pin.md) holds the dual-pin decision (Flink 2.1.3 here vs event-counts' 2.2.1) and its upgrade trigger.

## Shape

- `LakeEvent` — immutable record + event-type vocabulary check (+ ingestion stamp)
- `EventParser` — Jackson wire mapping, malformed input yields empty (never crashes the job)
- `EventsSchema` — the table contract: five columns, field ids are schema identity (append-only evolution), day-partition on `created_at`
- `LakeRows` — positional mapping to Flink internal rows (column order IS the contract)
- `LakeCatalog` — JDBC-catalog + S3FileIO property wiring, idempotent ensure-table
- `EventsLakeJob` — source → parse → map → `IcebergSink`; exactly-once via checkpoints

## Boundaries

- Raw landing zone only — dedup, enrichment, and aggregates belong to other jobs; the table must stay a faithful replayable record of what the gateway emitted.
- Parser is intentionally sibling-local to event-counts (schemas evolve separately; extraction waits for a third consumer).
- Catalog lives in the same Postgres as replicated CDC tables — teardown orderings treat both as stateful.

## Verification

12 unit tests (parser incl. null-literal/null-`created_at` poison cases; positional row mapping with micros-precision instant round-trip; schema order/type/partition guards + rowType-vs-schema drift guard). **E2E-proven on THINKBOOK (2026-08-26)**: 9 gateway events → exactly 2 Iceberg snapshots (added-records 5+4), Parquet in day-partition dirs, catalog row registered; steady RSS 493 MiB. Cold-start caveat: tail-offset source + ephemeral checkpoints means restarts skip downtime gaps (documented in README; durable backend deferred to deployment-shape ADR).
