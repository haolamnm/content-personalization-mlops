---
title: "ADR 0004 — Polyglot by Concern: Language Ownership Map"
id: adr-0004
date: 2026-08-25
type: adr
status: accepted
tags: [polyglot, java, python, go, rust, typescript, streaming, contracts]
related:
  - ./0001-content-personalization-theme.md
  - ./0003-ram-budgeted-local-infrastructure.md
  - ./0005-sveltekit-over-nextjs.md
---

# ADR 0004 — Polyglot by Concern: Language Ownership Map

## Status

Accepted (2026-08-25). Changes require a superseding ADR, not per-task improvisation.

## Context

The workspace optimizes for two things at once: an **optimal** production-grade pipeline (right tool per job, measured performance and memory) and **maximum learning** (each language owns a distinct runtime paradigm). The machine constraint ([ADR 0003](./0003-ram-budgeted-local-infrastructure.md); live facts in `COMPUTER.md`) makes runtime footprint a first-class selection criterion. Kafka-centric architecture also implies living in the JVM ecosystem where that ecosystem is strongest.

## Decision

Each concern owns exactly one language; services never share libraries across seams — they talk through contracts (OpenAPI + Avro/JSON Schema).

| Concern | Language | Version policy | Why this tool |
|:---|:---|:---|:---|
| Stream processing: Flink jobs + one Kafka Streams enrichment service | **Java** | JDK 25 LTS; Kafka 4.x / Flink 2.x majors pinned per-phase in compose/build files | JVM-native where the JVM genuinely wins: Flink and Kafka Streams are Java-first (docs, operators, ecosystem); Debezium/Kafka run on the JVM though config-only |
| ML plane: Feast feature defs, Ray Train/Tune, MLflow tracking, FastAPI/Ray Serve serving internals | **Python** | 3.14 | Non-negotiable ecosystem gravity — Feast/Ray/MLflow are Python-first; the ML plane is Python's home turf |
| Event gateway, app-facing BFF, simulators/load generators | **Go** | 1.27 | Goroutine-cheap concurrency at the edge; ~tens-of-MB RSS services keep ADR 0003 budgets honest; single static binaries deploy clean |
| Retrieval/ranking hot path: Redis feature join + light scoring under strict tail latency | **Rust** | 1.98, edition 2024 | P99-latency-critical hop with zero-GC pauses and minimal memory headroom cost; the one service where systems programming pays rent |
| Frontend | **TypeScript** (strict) on SvelteKit / Node 24 LTS | latest TS via package.json pin | See [ADR 0005](./0005-sveltekit-over-nextjs.md); Node 24 is Active LTS ("Krypton") |
| Lakehouse/DWH transforms | **SQL** | engine-pinned | Iceberg/DWH transformations are SQL's home |
| Contracts | OpenAPI + Avro/JSON Schema | — | Cross-language seams are versioned artifacts, generated clients where available |

Learning narrative (the deliberate design): five languages, five paradigms — JVM streaming (Java), data/ML (Python), concurrent network services (Go), systems latency (Rust), compiled reactive UI (TypeScript/Svelte). No language is decorative; each owns the stage where it is objectively strongest or is the industry default.

## Alternatives Considered

1. **Single-language monorepo (all-Python)**: rejected — simplest to write, worst to operate here: extra RAM per component, no latency story at the hot path, and the learning goal collapses.
2. **JVM-first services (Spring Boot everywhere)**: rejected — each JVM service costs 0.5–1 GB+ against [ADR 0003](./0003-ram-budgeted-local-infrastructure.md); Java stays only where the ecosystem demands it.
3. **Node/TS backend services**: rejected for owned backends — Go/Rust win RSS and tail latency for gateway/hot-path roles; TypeScript concentrates in the FE where its type system carries the most weight.
4. **Kotlin instead of Java**: deferred — reasonable, but Kafka/Flink learning material, examples and operator ergonomics are Java-first; plain Java tracks the source material closest.
5. **Zig/C++ instead of Rust**: rejected — memory safety plus cargo maturity are decisive for a solo-learning codebase.
6. **Scala for Flink**: rejected — Flink's future investment and docs are Java-first; Scala adds a sixth paradigm without a distinct home.

## Consequences

- Build/tooling matrix arrives incrementally: Maven (Phase 1–2; chosen over Gradle — no persistent daemon RAM against [ADR 0003](./0003-ram-budgeted-local-infrastructure.md), and Flink/Kafka Streams docs are Maven-first), uv/pyproject (Phase 2), Go modules (Phase 1), Cargo (Phase 4), Bun with pnpm fallback (Phase 5). No upfront scaffolding of all five.
- Every cross-seam call needs a versioned contract artifact before either side exists; contract drift is a review-blocking defect.
- CI will eventually need per-language caches/runners — deferred until `platform/` exists.
- Version pins live in manifests (`go.mod`, `pyproject.toml`, `Cargo.toml`, `package.json`, build file, compose files) — never from memory; majors bump deliberately with a decision-log row.
