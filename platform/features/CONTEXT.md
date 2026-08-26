---
title: "Feature Platform Context"
id: feature-platform-context
date: 2026-08-26
type: context
status: active
tags: [python, feast, iceberg, redis, features]
related:
  - ../../CONTEXT-MAP.md
  - ../../docs/agents/architecture/ml-platform.md
  - ../../docs/agents/architecture/domain-contracts.md
---

# Feature Platform (`platform/features/`)

The Feature Platform owns the user/item feature contract used by future training and retrieval. Its public seam is a Feast FeatureService named `ranking_features`, backed by a causally safe seven-day interaction snapshot.

## Source and stores

- Iceberg `mlops_lake.events_raw` on MinIO is the source of truth. The adapter resolves the current JDBC-catalog metadata file and reads the snapshot with DuckDB.
- Feast 0.65's Dask offline store performs point-in-time joins over the generated Parquet projections; the explicit adapter keeps the existing Iceberg JDBC catalog and MinIO layout as the source boundary.
- Feast's Redis online store holds only the latest value per independent user or item entity key; it is not a historical source, and its keys expire after the seven-day feature TTL. On k3s it is `mlops-redis-master.mlops-data.svc.cluster.local:6379` with password authentication.

## Feature contract

`user_interaction_features` exposes the user counts and `item_interaction_features` exposes the item counts; `ranking_features` combines them for consumers. Each event emits a strict-before event-time row, while delayed events also emit a post-ingestion availability row so online reads see available history without leaking labels. Rolling counts use heap-backed expiry rather than rescanning each entity history.

## Verification

The focused tests prove Feast historical retrieval returns the feature values available at each entity timestamp, including delayed events and unseen user/item pairings. Online parity is proven by materializing the separate user and item views into authenticated Redis and reading their independent keys. The full live gate requires the k3s Redis service, the existing Iceberg catalog, and a current raw-event snapshot.
