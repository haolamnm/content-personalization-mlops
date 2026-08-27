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
- The standing THINKBOOK connectors run as Strimzi `KafkaConnector` resources in `mlops-data`; passwords are resolved through the Kubernetes Secret ConfigProvider. PostgreSQL uses its replication role, while MongoDB uses the `mongodb-auth` root credential for this learning runtime. Compose remains the MACBOOK fallback.
- Envelope lands on `mlops.public.interactions`; insert proven end-to-end on THINKBOOK.
- MongoDB runs as the single-node `rs0` replica set required by change streams. Content catalog writes from `mlops_catalog.content_items` land on `mlops_mongodb.mlops_catalog.content_items`; insert proven end-to-end on THINKBOOK.

## Pins & quirks

- `quay.io/debezium/connect:3.6.1.Final` — newest stable; Docker Hub mirror stale at 3.0 (quay is authoritative for this artifact).
- Mongo connector change streams require a replica set; a standalone MongoDB server has no oplog/change-stream source. The k3s chart therefore runs one `rs0` member, while the Compose fallback remains standalone and does not claim Mongo CDC.
- Mongo connector certified only for Mongo 6.0/7.0/8.0 → that's why mongo stays on 8.0.x despite newer stable existing.
- Mongo ≥ kernel 6.19 crash-loops (`SERVER-121912`) without `GLIBC_TUNABLES=glibc.pthread.rseq=1` in the service environment — keep on any mongo bump until upstream fixes.

The k3s Connect image is built from the Strimzi Kafka image and copies only Debezium's PostgreSQL and MongoDB plugins from `quay.io/debezium/connect:3.6.1.Final`; the Compose image cannot be used directly because it lacks Strimzi's Connect entrypoint.
