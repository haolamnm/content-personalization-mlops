---
title: "CDC with Debezium"
id: agents-knowledge-cdc-debezium
date: 2026-08-25
type: knowledge
status: active
tags: [cdc, debezium, postgres, mongo]
related:
  - ../knowledge/image-pins.md
  - ../../../platform/infra/compose.cdc.yaml
---

# CDC with Debezium

## Wiring pattern

- Postgres side: `wal_level=logical` in the data group; publication + slot created by an **idempotent PUT registration** against the Connect REST API — reruns converge instead of duplicating connectors.
- Connect config is **flat** (no nested spec object): keys like `"name"`, `"database.hostname"` sit alongside `"connector.class"`. The API rejects the nested shape silently-looking but loudly.
- The standing THINKBOOK connector runs as a Strimzi `KafkaConnector` in `mlops-data`; its password is resolved through the Kubernetes Secret ConfigProvider and its PostgreSQL user has the `REPLICATION` attribute. Compose remains the MACBOOK fallback.
- Envelope lands on `<schema>.<table>` topic (`public.interactions`); insert proven end-to-end on THINKBOOK.

## Pins & quirks

- `quay.io/debezium/connect:3.6.1.Final` — newest stable; Docker Hub mirror stale at 3.0 (quay is authoritative for this artifact).
- Mongo connector certified only for Mongo 6.0/7.0/8.0 → that's why mongo stays on 8.0.x despite newer stable existing.
- Mongo ≥ kernel 6.19 crash-loops (`SERVER-121912`) without `GLIBC_TUNABLES=glibc.pthread.rseq=1` in the service environment — keep on any mongo bump until upstream fixes.

The k3s Connect image is built from the Strimzi Kafka image and copies only Debezium's PostgreSQL and MongoDB plugins from `quay.io/debezium/connect:3.6.1.Final`; the Compose image cannot be used directly because it lacks Strimzi's Connect entrypoint.
