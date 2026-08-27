# MLOps Zero→Hero

> **Learn every layer by building it.** One theme — content personalization — carried from first event to a production-grade platform.

A workspace where an MLOps platform is built from zero: user interactions flow through Debezium CDC → Kafka → Java stream jobs (Flink + Kafka Streams) → MinIO/Iceberg lakehouse → Feast features (offline Iceberg, online Redis) → Ray Train + MLflow → FastAPI/Ray Serve models behind a Rust retrieval hot path → Go BFF → SvelteKit app — observed end-to-end (OpenTelemetry/SigNoz, Prometheus/Grafana) and analyzed in Superset. The full north-star architecture is documented in [`docs/agents/architecture/north-star.md`](docs/agents/architecture/north-star.md).

## Status

Phase 2 of 9 (phases 0–8; feature platform): architecture decisions are locked, the Phase 1 data foundation is live, and the Feature Platform seam is implemented in `platform/` — Feast user/item features with Iceberg point-in-time history and Redis online materialization. The THINKBOOK k3s cutover is complete; training, serving, app, observability, and analytics remain reserved for later phases.

## Polyglot by concern

| Concern | Language |
|---|---|
| Stream processing (Flink job, one Kafka Streams service) | Java 25 LTS |
| ML plane (Feast, Ray, MLflow, FastAPI/Ray Serve) | Python 3.14 |
| Event gateway, BFF, simulators | Go 1.27 |
| Retrieval/ranking hot path | Rust 1.98 |
| Frontend | TypeScript (SvelteKit, Bun toolchain, Node 24 runtime) |

Rationale and rejected alternatives per language: [ADR 0004](docs/adr/0004-polyglot-language-per-concern.md). FE framework choice: [ADR 0005](docs/adr/0005-sveltekit-over-nextjs.md).

## Repository layout

- [`AGENTS.md`](AGENTS.md) — how agents work here: instruction hierarchy, rules, skills, verification gates
- [`CONTEXT-MAP.md`](CONTEXT-MAP.md) — pipeline bounded contexts and ubiquitous language
- [`docs/AGENTS.md`](docs/AGENTS.md) — documentation hub (ADRs, decision log, generated catalogs)
- `.notes/`, `.repos/`, `.worklog/` — local-only learning material, reference clones, session state (gitignored by design)

## Documentation

- Architecture index: [`docs/agents/architecture/index.json`](docs/agents/architecture/index.json)
- North star: [`docs/agents/architecture/north-star.md`](docs/agents/architecture/north-star.md)
- ADRs: [`docs/adr/index.json`](docs/adr/index.json) · Decision log: [`docs/agents/decision-log.md`](docs/agents/decision-log.md)
- Full catalog: [`docs/index.json`](docs/index.json)
