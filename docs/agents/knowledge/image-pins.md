---
title: "Image Pins & Why"
id: agents-knowledge-image-pins
date: 2026-08-25
type: knowledge
status: active
tags: [images, pins, docker, flink, kafka]
related:
  - ../knowledge/compose-groups-and-ram.md
  - ../../adr/0003-ram-budgeted-local-infrastructure.md
---

# Image Pins & Why

Pins are registry-verified at adoption, never from memory. Compose files carry the versions; this doc carries the *reasons* so bumps are informed.

## Data group

| Image | Pin | Why pinned here |
|:---|:---|:---|
| `postgres` | 18.6 | current stable at adoption; volume must mount `/var/lib/postgresql` — postgres:18 moved PGDATA to `/var/lib/postgresql/18/docker`, legacy-path mounts break or silently fail to persist |
| `mongo` | 8.0.29 | Debezium certifies Mongo 6.0/7.0/8.0 only (3.7 connector still alpha) — 8.3.8 "current stable" would block CDC |
| `apache/kafka` | 4.3.1 | KRaft-only line; see [kafka-bus](./kafka-bus.md) for listener scheme |
| `minio/minio` | `RELEASE.2025-09-07T16-13-09Z` | community edition archived upstream (repo read-only since 2026-04-25, final security release never published as a tag); last pullable tag; revisit only if a phase demands newer MinIO |

## Streaming

Per-module pins ([ADR 0008](../../adr/0008-iceberg-lake-sink-dual-pin.md)): the two jobs run different Flink majors because `iceberg-flink-runtime` ships per-major jars.

| Artifact | Pin | Why |
|:---|:---|:---|
| Flink (event-counts) | 2.2.1 | newest minor with a matching Kafka connector build (see below) |
| Flink (events-lake) | 2.1.3 | newest patch of the 2.1 line — the latest Iceberg-supported major at adoption |
| `flink-connector-kafka` (event-counts / events-lake) | 5.0.0-2.2 / 5.0.0-2.1 | connector releases track specific Flink minors; matched pairs, no drift (review-blocking per java rules) |
| Kafka clients | 4.2.x (transitive, both) | compatible with broker 4.3.1 |
| iceberg-flink-runtime-2.1 + aws-bundle (events-lake) | 1.11.0 | latest release; no `-2.2` runtime exists yet — **trigger**: bump both jobs to one version when 1.12.0 ships |
| Runtime image | `eclipse-temurin:25-jre`, digest `sha256:f9e65324a37f28209ce7dd0e5149a7aa954520ed936fb87813cf6ded2400a112` verified | JDK 25 LTS per ADR 0004; both streaming jars |

## CDC

`quay.io/debezium/connect:3.6.1.Final` — newest stable; Docker Hub mirror stale at 3.0, so quay is the source of truth for this artifact.

## Kubernetes cutover

THINKBOOK's standing data plane uses Strimzi 1.1.0/Kafka 4.3.0, CloudNativePG PostgreSQL 18.6, MinIO chart 5.4.0 with `minio/minio:RELEASE.2025-09-07T16-13-09Z`, and MongoDB chart 16.5.45 with `bitnamilegacy/mongodb:8.0.13-debian-12-r0`. The Mongo image is a logical-restore target; no Compose Mongo files are reused.
