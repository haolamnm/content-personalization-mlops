---
title: "ADR 0006 — THINKBOOK as Standing Remote Deployment Target"
id: adr-0006
date: 2026-08-25
type: adr
status: accepted
tags: [infrastructure, deployment, tailscale, thinkbook]
related:
  - 0003-ram-budgeted-local-infrastructure.md
---

# ADR 0006 — THINKBOOK as Standing Remote Deployment Target

## Status

Accepted (2026-08-25).

## Context

ADR 0003 sized compose profile groups around MACBOOK's constrained memory: one group at a time, no cross-group live integration. A second Linux machine was provisioned as a remote runtime (hardware, OS, and network facts: `.computers/THINKBOOK.md`, developer-local), later joined to a Tailscale mesh. ADR 0003's alternative 2 ("remote sandbox for heavy phases — revisit if a phase proves impossible locally") is now revisited early: the constraint is not impossibility but iteration speed and cross-group integration.

## Decision

THINKBOOK is the standing remote runtime for this repo's compose groups:

- **Transport**: Tailscale is the primary path (`ssh thinkbook`, MagicDNS name). Home-LAN direct IP is an SSH-only fallback; all service ports remain loopback-bound on the box and are never exposed to the LAN.
- **Deploy model**: push-from-Mac. `git push thinkbook main` with `receive.denyCurrentBranch=updateInstead`; the box holds pre-existing personal SSH keys with GitHub read access (verified) but no gh CLI and no stored tokens. Mac remains the sole authoring/pushing identity.
- **Worktree**: `~/Workspaces/MLOps`, mirrors main.
- **Secrets**: per-box `.env` (gitignored), strong random values generated at provisioning; never synced from the Mac.
- **Port policy**: compose host ports are `${VAR:-default}` overridable so both boxes coexist with local services (ThinkBook runs system postgresql on 5432 → uses `POSTGRES_HOST_PORT=15432`); container-network addresses unchanged. Exception: Kafka's host port is fixed at `29094` because the broker advertises it — overriding it would desync advertisement from listener.
- **Measurement**: RSS actuals land in the running box's fact file `Measured artifacts` section — §5 consistently (`.computers/MACBOOK.md` / `.computers/THINKBOOK.md`, both developer-local).
- **Scope wall**: WORKSTATION (CloudThinker GCP VM) stays out of MLOps entirely (`.computers/WORKSTATION.md`, developer-local).

MACBOOK remains the authoring box; its one-group-at-a-time rule binds *per machine* — THINKBOOK's budget allows multiple groups concurrently there, to be expanded deliberately as measurements accumulate.

## Alternatives Considered

1. **Mac-only forever**: rejected — cross-group integration (CDC→streaming→serving) is impossible under MACBOOK's memory ceiling (specs: `.computers/MACBOOK.md`); swap-thrash is arithmetic, not pessimism (ADR 0003).
2. **gh-authenticated clone on ThinkBook**: rejected for now — stores a GitHub token on the deploy box for no capability we lack; revisit only if ThinkBook must open PRs itself.
3. **Cloud VM instead**: deferred again — Tailscale + spare hardware removed the cost/friction that motivated deferral in ADR 0003.

## Consequences

- Cross-group live integration becomes possible (staged on one box) — unblocks `feat/cdc-wiring` against a running data group.
- ADR 0003's group table gains a second venue column implicitly: estimates now get confronted on both machines, recorded separately per box.
- Tailscale becomes infrastructure dependency for deployments; SSH-over-LAN is the headless fallback when both devices share the home network; service ports never leave loopback.
