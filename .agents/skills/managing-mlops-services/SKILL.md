---
name: managing-mlops-services
description: RAM-budget-aware lifecycle for local infrastructure groups on this 16 GB machine via OrbStack — preflight checks, starting exactly one compose profile group, health checks, recording measured memory, and teardown. Use whenever any docker compose up/down is about to happen.
---

# Run the Local Stack (one group at a time)

The machine cannot host the full stack ([ADR 0003](../../../docs/adr/0003-ram-budgeted-local-infrastructure.md)). Exactly ONE profile group runs at a time; groups are disjoint.

## Groups (planning estimates — your measurements replace them)

| Group | Members | Planning est. |
|:---|:---|:---|
| core-data | PostgreSQL, MongoDB, Debezium, Kafka (KRaft), MinIO | ~3–4 GB |
| streaming | Flink jobmanager/taskmanager (+ Kafka if down) | ~2–3 GB |
| ml | Ray head/worker, MLflow, Feast | ~2–3 GB training |
| serving | Redis, Elasticsearch, Rust/Go/Python services | ~1.5–2 GB |
| app | SvelteKit build, NGINX, BFF | <0.5 GB |
| obs-light | Prometheus, Grafana, Vector | ~0.5–1 GB |
| obs-heavy | SigNoz stack alone | ~2–3 GB |
| analytics | Superset alone | ~1–2 GB |

## Workflow

1. **Preflight (mandatory)**: `docker ps` (must be empty or only the target group), `memory_pressure | head -20`, `docker stats --no-stream`. If another group is up → stop it first (`docker compose ... down`). Ask before running anything beyond obs-light if free memory looks tight.
2. **Start one group**: `docker compose -f platform/infra/<group>.yaml up -d` (compose files arrive in Phase 1). Validate first: `docker compose -f <file> config -q`.
3. **Health-check every member** before declaring success — each service gets an explicit check (HTTP endpoint, `kafka-topics --list`, `mc ready`, etc.). No "container is running" hand-waving.
4. **Capture actuals**: `docker stats --no-stream` RSS per container → append one line to `COMPUTER.md` §5 (`date · group · container · RSS`). Estimates graduate here or die ([Principle 5](../../../AGENTS.md)).
5. **Teardown**: `down` when the session's work with the group ends; `-v` only when the group's data is disposable — never blindly.

## Hard rules

- Never two groups at once, even "just briefly".
- OrbStack memory is dynamic ([`COMPUTER.md`](../../../COMPUTER.md) §3) — set an explicit cap before obs-heavy/analytics rather than trusting reclaim mid-run.
- If a group OOMs or thrashes: stop, record what happened in §5, and re-plan sizes in ADR 0003 — don't just retry.
