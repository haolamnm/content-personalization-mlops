# MLOps Zero→Hero

> **Learn every layer by building it.** One theme — content personalization — carried from first event to a production-grade platform.

A workspace where an MLOps platform is built from zero: user interactions flow through Debezium CDC → Kafka → Java stream jobs (Flink + Kafka Streams) → MinIO/Iceberg lakehouse → Feast features (offline Iceberg, online Redis) → Ray Train + MLflow → FastAPI/Ray Serve models behind a Rust retrieval hot path → Go BFF → SvelteKit app — observed end-to-end (OpenTelemetry/SigNoz, Prometheus/Grafana) and analyzed in Superset.

## Status

Phase 0 of 9 (phases 0–8; foundations): architecture decisions locked ([`docs/adr/`](docs/adr/)), toolchains installed, reference implementation under study. No runtime code yet — the build lands in `platform/` from Phase 1.

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
- [`docs/README.md`](docs/README.md) — documentation hub (ADRs, decision log, generated catalogs)
- `.notes/`, `.repos/`, `.worklog/` — local-only learning material, reference clones, session state (gitignored by design)

## Documentation

- ADRs: [`docs/adr/index.json`](docs/adr/index.json) · Decision log: [`docs/agents/decision-log.md`](docs/agents/decision-log.md)
- Full catalog: [`docs/index.json`](docs/index.json)
