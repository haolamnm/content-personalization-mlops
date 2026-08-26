---
title: "ADR 0008 — Iceberg Lake Sink via Dual-Pin (Flink 2.1 + Iceberg 1.11)"
id: adr-0008
date: 2026-08-26
type: adr
status: accepted
tags: [streaming, iceberg, lakehouse, minio, flink]
related:
  - 0003-ram-budgeted-local-infrastructure.md
  - ../../docs/agents/knowledge/flink-streaming.md
  - ../../docs/agents/knowledge/image-pins.md
---

# ADR 0008 — Iceberg Lake Sink via Dual-Pin (Flink 2.1 + Iceberg 1.11)

## Status

Accepted (2026-08-26). Owner approved the dual-pin approach after reviewing the compatibility fork.

## Context

Phase 1's last open item lands raw gateway events as an Apache Iceberg table on MinIO. The streaming plane is pinned to Flink 2.2.1 ([flink-streaming.md](../agents/knowledge/flink-streaming.md)), but Apache Iceberg 1.11.0 (latest release, May 2026) ships Flink runtimes only for 1.20 / 2.0 / 2.1 — there is no `iceberg-flink-runtime-2.2`. The Iceberg dev list has converged on Flink 2.2 support landing in **Iceberg 1.12.0**, not yet released at decision time.

The reference repo offers no pattern to copy: its "data lake" is a Kafka Connect S3 sink dumping JSON files into buckets — no table format, no ACID, no schema.

## Decision

**Two jobs, two pins — each an officially supported pair, never a beta artifact:**

| Job | Flink | Iceberg runtime | Rationale |
|:---|:---|:---|:---|
| event-counts | 2.2.1 | — (untouched) | Proven e2e; no reason to churn |
| events-lake (new) | 2.1.3 | `iceberg-flink-runtime-2.1:1.11.0` | Official pair from the same 5.0.0 connector line (`flink-connector-kafka:5.0.0-2.1`) |

Jobs are separate containers with separate fat jars — they share no classpath, so mixed versions cost nothing operationally.

**Upgrade trigger**: when Iceberg 1.12.0 ships with `iceberg-flink-runtime-2.2`, bump events-lake to Flink 2.2.x + that runtime in one small PR and collapse back to a single streaming pin.

**Lakehouse shape**:

- **Catalog**: Iceberg **JDBC catalog** backed by the existing Postgres (`data` group) — production-realistic (managed-Postgres catalogs are common), zero new services, survives restarts.
- **Warehouse**: `s3://mlops-lake/` on MinIO, file IO through Iceberg's `aws-bundle` with endpoint override (S3-compatible, path-style).
- **Table**: `mlops_lake.events_raw`, append-only, schema = gateway envelope (user_id, item_id, event_type, created_at timestamptz) plus ingested_at timestamptz stamped at parse time, partitioned by **days(created_at)**.
- **Commit semantics**: Iceberg commits ride Flink checkpoints (exactly-once); small-file pressure mitigated by `write.target-file-size-bytes` and deferred compaction (tracked follow-up once data volume justifies it).

## Alternatives Considered

1. **Wait for Iceberg 1.12.0** (~weeks): keeps one Flink version but blocks Phase-1 completion on someone else's calendar; rejected.
2. **Unofficial `-2.2` runtime built from Iceberg main**: bleeding-edge yak-shave inside a learning project; rejected on Principle 5 grounds (nothing to prove stability).
3. **Run iceberg-flink-runtime-2.1 jar on Flink 2.2.1 unverified**: cross-minor binary compatibility is undocumented for Iceberg; would violate prove-by-running unless we did the compat matrix ourselves; rejected.
4. **Kafka Connect S3 sink like the reference repo**: files without a table format — no ACID commits, no schema evolution, exactly the lakehouse gap this phase exists to close; rejected.
5. **Hadoop catalog**: no external dependency but deprecated trajectory and known multi-engine hazards; JDBC catalog is the same effort with better habits.
6. **REST catalog (Nessie/Lakekeeper)**: adds a service to babysit before branching/warehouse-management lessons are needed; revisit if catalog branching becomes a Phase-2+ need.

## Consequences

- Two streaming jobs run as separate containers but share **one JVM base image**; [image-pins](../agents/knowledge/image-pins.md) carries it and both module pin sets with the trigger noted.
- `events-lake` tests and e2e proof run against Flink 2.1.3 semantics — the embedded-watermark constraint documented in [flink-streaming](../agents/knowledge/flink-streaming.md) applies identically (parallelism 1 embedded).
- Postgres gains a non-CDC role (catalog tables alongside replicated business tables) — backup/teardown orderings must treat both as stateful.
- Compaction/maintenance is explicitly deferred, not forgotten: revisit when partition counts or file counts make scans visibly slow.
