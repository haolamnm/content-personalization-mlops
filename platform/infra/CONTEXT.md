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
| Kafka (KRaft) | `apache/kafka:4.3.1` | 29092 | broker-api-versions |
| MinIO | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | 9000 / 9001 | `mc ready local` |

Pin rationale: MongoDB is 8.0.x, not the newer 8.3-series, because Debezium 3.7 certifies Mongo 6.0/7.0/8.0 only — CDC wiring lands in the next branch. MinIO's community repo was archived upstream (2026-04-25); this tag is the last pullable community image.

## Boundaries

- Debezium Connect is a member of the *cdc* slice, not data — it arrives with `feat/cdc-wiring`.
- Credentials come from root `.env` (copy `.env.example`); no secrets in compose files.
- Host ports bind `127.0.0.1` only — LAN-inaccessible by default; relax per-service if a remote client ever needs direct reach.
- Measured RSS goes to root `COMPUTER.md` §5 once the group first runs.
