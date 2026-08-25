---
title: "ADR 0003 — RAM-Budgeted Local Infrastructure"
id: adr-0003
date: 2026-08-25
type: adr
status: accepted
tags: [infrastructure, docker-compose, resource-budget, macos]
related:
  - ../../AGENTS.local.md
  - ../../.agents/rules/resource-budget.md
  - ../../.agents/skills/managing-mlops-services/SKILL.md
---

# ADR 0003 — RAM-Budgeted Local Infrastructure

## Status

Accepted (2026-08-25). Constraint is physical, not negotiable.

## Context

The target stack names ~20 services; several are JVM-heavy (Kafka brokers, Debezium Connect, Flink TaskManager, SigNoz's ClickHouse, Superset), realistically 0.5–2 GB RSS each. The dev machine is RAM-constrained (exact specs: root `COMPUTER.md`, developer-local) and runs containers through OrbStack's Linux VM. Starting everything simultaneously guarantees swap-thrash or a dead machine — this is arithmetic, not pessimism.

## Decision

Local infrastructure runs as **disjoint compose profile groups**, sized so one group fits comfortably in RAM:

| Group | Members (typical) | Planning estimate |
|:---|:---|:---|
| core-data | PostgreSQL, MongoDB, Debezium, Kafka (KRaft), MinIO | ~3–4 GB |
| streaming | Flink jobmanager/taskmanager (+ Kafka if not already up) | ~2–3 GB |
| ml | Ray head/worker, MLflow, Feast | ~2–3 GB while training |
| serving | Redis, Elasticsearch, Rust/Go/Python services | ~1.5–2 GB |
| app | SvelteKit build, NGINX, BFF | <0.5 GB |
| obs-light | Prometheus, Grafana, Vector | ~0.5–1 GB |
| obs-heavy | SigNoz stack alone (ClickHouse + OTel collector + UI) | ~2–3 GB |
| analytics | Superset alone | ~1–2 GB |

Rules: exactly ONE group at a time; previous group goes `down` before the next starts; preflight/postflight memory checks are mandatory; measured actuals replace estimates in the skill doc. Where we control code, prefer low-RSS runtimes (Go/Rust services over extra JVM instances) — see [ADR 0004](./0004-polyglot-language-per-concern.md).

## Alternatives Considered

1. **Run everything, accept swap**: rejected — macOS unified memory thrashing makes the whole machine unusable, not just slow.
2. **Remote/cloud sandbox for heavy phases**: deferred, not chosen — adds cost/network friction; revisit only if a phase proves impossible locally.
3. **Drop heavyweight services (SigNoz, Flink)**: rejected — contradicts the learn-everything goal; the profile discipline lets us keep them, just sequentially.

## Consequences

- No cross-group live integration testing; end-to-end runs must be staged group-by-group or done in a later cloud pass.
- Estimates above are planning numbers until measured — `managing-mlops-services` records actuals (Principle 5).
- OrbStack allocates VM memory dynamically; an explicit cap is preferred before heavy groups (value recorded in `COMPUTER.md` §3 once set).
