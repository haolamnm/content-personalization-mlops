---
title: "ADR 0007 — Kubernetes Adoption: k3s on THINKBOOK, Helm-First"
id: adr-0007
date: 2026-08-26
type: adr
status: accepted
tags: [infrastructure, kubernetes, k3s, helm, thinkbook]
related:
  - 0003-ram-budgeted-local-infrastructure.md
  - 0006-thinkbook-remote-deployment-target.md
  - ../../.agents/rules/resource-budget.md
---

# ADR 0007 — Kubernetes Adoption: k3s on THINKBOOK, Helm-First

## Status

Accepted (2026-08-26). Forks decided with owner: timing chosen by Hao Lam; distro/packaging/delivery delegated to agent rationale (owner new to Kubernetes — this ADR doubles as the written rationale to learn from).

## Context

The Phase-1 compose stack is live and proven (CDC → Kafka → Flink end-to-end on THINKBOOK). Two standing constraints shape any runtime change: [ADR 0003](./0003-ram-budgeted-local-infrastructure.md)'s one-group-at-a-time RAM discipline and [ADR 0006](./0006-thinkbook-remote-deployment-target.md)'s push-from-Mac deployment model. The owner wants Kubernetes adopted as the platform layer alongside the compose era, with **Helm charting folded in as an explicit learning goal**.

Orientation (one line each, since every candidate was new to the owner):

- **kind** — real Kubernetes nodes running *inside* Docker containers; the CNCF-conformant CI standard; ephemeral by nature.
- **k3d** — the same lightweight k3s, also wrapped in Docker for fast create/delete clusters.
- **microk8s** — Canonical's snap-packaged Kubernetes; convenient on Ubuntu, awkward on Fedora.
- **Talos Linux** — an immutable, API-only operating system that *is* Kubernetes; deep ops learning, but wants dedicated hardware.
- **k3s** — a single-binary, production-grade distribution (~0.5–1 GiB overhead) running as a plain systemd service; bundles a LoadBalancer (ServiceLB) and Traefik; the de-facto standard for edge/single-node clusters.

RAM arithmetic makes coexistence a non-issue on the deploy box: measured idle data group ≈ 517 MiB, Flink trio ≈ 2.2 GiB total (`.computers/THINKBOOK.md` §5), k3s control plane ~1 GiB — against 27 Gi usable. The binding constraint is **operational clarity** (one source of truth for Kafka), not memory.

## Decision

1. **Distro**: k3s, single node, on THINKBOOK — the standing cluster. MACBOOK stays authoring-only: `kubectl`/`helm` run from the Mac against the cluster over Tailscale (kubeconfig copied once, loopback-bindings respected per ADR 0006). Compose remains the Mac dev venue indefinitely under the unchanged one-group rule.
2. **Timing — cut over at the phase edge**: remaining Phase-1 scope (including the MinIO/Iceberg sink) completes on compose first. The cutover — k3s bootstrap → migrate the data group → re-home gateway and Flink job as Deployments — is its own work package at the Phase 1→2 boundary. No dual runtimes on THINKBOOK after cutover: two brokers means two truths, and split-brain Kafka is the failure mode this sequencing exists to avoid.
3. **Packaging — operators + charts for infra, hand-written charts for owned services**: Strimzi (Kafka broker plus KafkaConnect carrying Debezium via its CRDs), CloudNativePG (Postgres), the official MinIO chart; Mongo via community chart at migration time (operator only if its reconciliation model becomes a lesson worth having). Our own images — the Go event gateway, Flink jobs, everything downstream — get small hand-written Helm charts, one chart per service, `values` per venue (mac/thinkbook). No umbrella mega-chart.
4. **Delivery UX — Helm driven by Make over ssh**: targets mirror today's compose UX (`make k8s-data-up` …) wrapping `helm upgrade --install` / `kubectl apply`. Code deploy stays ADR 0006's `git push thinkbook main`; image rebuild + release upgrade is the manual follow-up. GitOps (Flux/ArgoCD) deferred with an explicit revisit trigger: Phase 8 hardening, or earlier if chart-count × env-count makes manual upgrades error-prone.
5. **Storage**: k3s's bundled local-path provisioner. PersistentVolumes are node-bound — an accepted single-box tradeoff, revisited only if a second node ever appears.
6. **Budget rule carries over**: [resource-budget](../../.agents/rules/resource-budget.md) discipline extends verbatim to namespaces/releases — one group live at a time, preflight/postflight checks via `kubectl top`, measured actuals recorded in `.computers/THINKBOOK.md` §5 as always.

## Alternatives Considered

1. **kind as the standing cluster** — best conformance story, worst always-on story (containers die with the host session mindset); rejected here, welcome back later as a throwaway chart-test rig.
2. **k3d instead** — identical engine to k3s but disposable by design; choosing it for the *standing* role would erase the always-on deployment narrative ADR 0006 established.
3. **microk8s** — snap lifecycle fights Fedora's defaults; k3s installs with one static binary and no store dependency.
4. **Talos** — the deeper lesson, wrong budget: it consumes a whole machine (or VM) and replaces the Fedora host story THINKBOOK already has.
5. **Switch mid-phase now** — abandons a working, freshly-proven pipeline mid-stream; owner explicitly chose the phase-edge cutover.
6. **Owned services on k8s, infra on compose forever** — permanent split-brain Kafka risk and a two-runtime tax on every future slice; rejected.
7. **Hand-rolled manifests for infra** — maximal StatefulSet mechanics, maximal yak-shaving; operators *are* how the industry runs stateful middleware, so we learn consumption there and spend hand-writing effort on services we own.
8. **Bitnami-style uniform charts for everything** — simplest values story, least transferable Kafka knowledge; Strimzi's CRD model reflects real production usage.
9. **GitOps from day one** — a reconciliation controller to babysit before any chart exists to reconcile; deferred with trigger above.

## Consequences

- **Learning debt is explicit**: the owner is new to Kubernetes, Helm, and operators — every migration PR pairs its diff with a `.notes/topics/` walkthrough of the concepts it introduced (the studying-mlops protocol applied to our own platform).
- Phase-1's definition grows by nothing; the cutover joins the roadmap as boundary work between Phases 1 and 2, gated on the Iceberg sink shipping on compose first.
- THINKBOOK §5 will gain k3s bootstrap measurements; ADR 0003's estimate-vs-measured loop continues on a third runtime surface.
- Topic identity resets at migration: Kafka topics and the Debezium connector registration are rebuilt in-cluster (dev-tier acceptance — offsets are disposable); the idempotent PUT registration flow already scripts this.
- Per-module CONTEXT docs gain a venue column (compose / k8s) as slices move, keeping drift visible rather than folklore.
- New runbook(s) land at bootstrap time (successor to the deploy-thinkbook runbook covering k3s admin, kubeconfig distribution, release upgrades).
