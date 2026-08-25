---
title: "Infra Context"
id: infra-context
date: 2026-08-25
type: context
status: active
tags: [infrastructure, docker-compose, data]
related:
  - ../../CONTEXT-MAP.md
  - ../../docs/adr/0003-ram-budgeted-local-infrastructure.md
---

# Infra (`platform/infra/`)

Compose-managed infrastructure groups ([ADR 0003](../../docs/adr/0003-ram-budgeted-local-infrastructure.md)): one file = one profile group; exactly one group runs at a time. Lifecycle rules live in the [`managing-mlops-services`](../../.agents/skills/managing-mlops-services/SKILL.md) skill; Makefile targets wrap its flow (preflight → up → health → stats → down).

## Groups

### data — `compose.data.yaml` · status: **defined, not yet run**

| Service | Image (pinned 2026-08-25) | Host port | Health check |
|:---|:---|:---|:---|
| PostgreSQL | `postgres:18.6` | 5432 | `pg_isready` |
| MongoDB | `mongo:8.0.29` | 27017 | `mongosh ping` |
| Kafka (KRaft) | `apache/kafka:4.3.1` | 29094 (host) · 9092 (mesh) | broker-api-versions |
| MinIO | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | 9000 / 9001 | `mc ready local` |

Pin rationale: MongoDB is 8.0.x, not the newer 8.3-series, because Debezium 3.7 certifies Mongo 6.0/7.0/8.0 only — and the live PostgreSQL CDC slice on THINKBOOK (cdc group below) depends on that certification. MinIO's community repo was archived upstream (2026-04-25); this tag is the last pullable community image.

### cdc — `compose.cdc.yaml` · status: **live on THINKBOOK**

| Service | Image (pinned 2026-08-25) | Host port | Health check |
|:---|:---|:---|:---|
| Debezium Connect | `quay.io/debezium/connect:3.6.1.Final` | 8083 | Connect REST `/connectors` |

Joins the data group's named network (`mlops-data`, external) so `postgres`/`kafka` hostnames resolve; bring-up order enforced by `make cdc-up` (starts postgres+kafka first, waits for connect health). Pin is 3.6.x, not the in-development 3.7 alphas, because 3.6.1.Final already ships Kafka 4.3 + PostgreSQL 18 support.

### gateway — `compose.gateway.yaml` · status: **live on THINKBOOK**

| Service | Image | Host port | Health check |
|:---|:---|:---|:---|
| event-gateway | `mlops/event-gateway:latest` (built from `platform/services/event-gateway`) | 8080 | `GET /healthz` |

First owned service (Go): `POST /events` validates and produces to topic `mlops.events.raw` keyed by `user_id`. `make topics-ensure` creates the topic explicitly — Kafka 4.x auto-create is disabled.

## Boundaries

- The sanctioned compose set is **data + cdc + gateway**; all three are whitelisted in the Makefile guard and any further project is refused. The one-group-at-a-time rule applies on MACBOOK; THINKBOOK permits the documented trio coexistence under its larger budget.
- Credentials come from root `.env` (copy `.env.example`); no secrets in compose files.
- Host ports bind `127.0.0.1` only — LAN-inaccessible by default; relax per-service if a remote client ever needs direct reach.
- Runtime boxes: groups are authored and first-measured on MACBOOK (RAM-capped, one group at a time); THINKBOOK is the standing deployment target over Tailscale (`ssh thinkbook`) for full-stack sessions — per-box facts in [`.computers/`](../../.computers/).
- Measured RSS goes to the running box's file §5 — MACBOOK §5 locally, THINKBOOK §5 remotely.
