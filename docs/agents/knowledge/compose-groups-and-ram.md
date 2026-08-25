---
title: "Compose Groups & RAM Discipline"
id: agents-knowledge-compose-groups
date: 2026-08-25
type: knowledge
status: active
tags: [compose, docker, ram, healthchecks]
related:
  - ../../adr/0003-ram-budgeted-local-infrastructure.md
  - ../../adr/0006-thinkbook-remote-deployment-target.md
  - ../../../.agents/rules/resource-budget.md
---

# Compose Groups & RAM Discipline

## Group model

One-word profile groups, one group at a time per box (THINKBOOK tolerates the sanctioned trio `data` + `cdc` + gateway). The Makefile `data-guard` whitelists exactly these — widening it is a deliberate act, synced with [CONTEXT-MAP](../../../CONTEXT-MAP.md) boundaries.

Measured reality beats estimates: idle data group ran ≈517 MiB against a ~2.5–3.5 GB planning guess (~6× high); Flink embedded job ≈366 MiB. Every new group gets a `docker stats --no-stream` reading recorded in `.computers/<BOX>.md`.

OrbStack (Mac) VM memory is dynamic — set an explicit cap before heavy groups rather than trusting reclaim mid-run; cap changes are deliberate acts.

## Gotchas banked

- **Bind-mount paths must contain `/`** (or `$PWD/`) — bare names become named volumes and mount as empty directories.
- **postgres:18 volume path**: mount `/var/lib/postgresql`, not the legacy `/var/lib/postgresql/data` — PGDATA moved to `/var/lib/postgresql/18/docker`.
- **Port offsets** where system services collide: ThinkBook's system postgresql owns 5432 → data group uses `POSTGRES_HOST_PORT=15432`; host-only Kafka listener lives on 29094.
- **Healthchecks through two quoting layers** (ssh → shell): prefer space-free probes (`find … -mmin -2 | grep -q chk`) over quoted time expressions that get stripped en route. Health = a real liveness signal (checkpoint freshness for stateful jobs), not just "process up".
- **Restart policies**: `unless-stopped` gives reboot self-heal for standing groups; one-shot dev containers use explicit `--rm`.
