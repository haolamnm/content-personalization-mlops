---
title: "Event Gateway Context"
id: event-gateway-context
date: 2026-08-25
type: context
status: active
tags: [go, gateway, ingestion]
related:
  - ../../CONTEXT-MAP.md
  - ../../.agents/rules/go-general.md
---

# Event Gateway (`platform/services/event-gateway/`)

Edge ingestion for interaction events ([ADR 0004](../../../docs/adr/0004-polyglot-language-per-concern.md): Go owns the edge). Accepts `POST /events` with `{user_id, item_id, event_type}`, validates against the platform vocabulary (impression/click/dwell/like/share), stamps `created_at`, and produces to Kafka topic **`mlops.events.raw`** keyed by `user_id` so per-user ordering survives partitioning.

## Shape

- `cmd/event-gateway/main.go` — wiring, graceful shutdown on SIGINT/SIGTERM
- `internal/gateway/` — domain type + validation + HTTP server; `Producer` is the outbound port (faked in tests)
- `internal/broker/` — franz-go adapter implementing the port; sync produce with 5s timeout

## Config

| Env | Default | Meaning |
|:---|:---|:---|
| `GATEWAY_ADDR` | `:8080` | listen address |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:29094` | host-run dev default; mesh uses `kafka:9092` |
| `GATEWAY_TOPIC` | `mlops.events.raw` | raw-event topic |

## Boundaries

- `/healthz` is **liveness only** (process up). Kafka readiness is enforced once at startup (fail-fast ping) and afterwards surfaces as 503 on `/events` — anything automating off the health signal must treat it accordingly.
- Raw topic only — enrichment/aggregation belongs to stream jobs; OLTP state changes flow through CDC, not this path.
- Bodies are capped at 64 KiB (`413` beyond); IDs are trimmed before keying so per-user Kafka ordering holds.
- Deployment: `platform/infra/compose.gateway.yaml` runs it on the data group's network; THINKBOOK first-class per [ADR 0006](../../../docs/adr/0006-thinkbook-remote-deployment-target.md).

## Verification

`go vet ./...`, `gofmt -l .`, `go test ./...` — table-driven handler + validation tests with fake producer; integration tests (tagged) come when Flink needs them.
