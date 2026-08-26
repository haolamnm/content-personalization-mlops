---
title: "Kubernetes Migration"
id: agents-knowledge-kubernetes-migration
date: 2026-08-26
type: knowledge
status: active
tags: [kubernetes, k3s, helm, migration, kafka]
related:
  - ../../adr/0007-kubernetes-adoption-k3s-helm.md
  - ../runbooks/deploy-k8s.md
---

# Kubernetes Migration

Working facts from the compose→k3s cutover (streaming plane first; data group last).

## The Kafka listener boundary (blocks in-cluster clients)

The compose broker advertises `PLAINTEXT_HOST://localhost:29094` — a client that bootstrap-connects via the node IP receives metadata redirecting it to `localhost:29094`, which inside a pod is the pod itself. **Ordinary pod networking cannot produce/consume across the boundary** until either Strimzi lands (data-group migration) or the broker gains a third listener advertising a routable address. Exception: `hostNetwork` pods share the node's namespace, so loopback works for them.

Dev-venue bridge: charts run with `hostNetwork: true` (+ `dnsPolicy: ClusterFirstWithHostNet`) so pods share the node's loopback where compose publishes 29094/15432/9000. This is explicitly a lossy dev-tier contract — production venue flips it to `false` once Kafka is in-cluster.

## Consumer-group cutover ordering

Two instances sharing a group split partitions silently. When moving a consumer: retire the docker-run container first (`docker rm -f …`), then `helm install` with the same group id — offsets live on the broker, so the group resumes where the container left off.

The **gateway** has a harder conflict: under `hostNetwork` it binds the node's port 8080, which the compose gateway already holds on loopback — installing before retiring guarantees CrashLoopBackOff. Same rule, stricter: retire first, always.

## Node-port exposure is decided by paired rich rules

Fedora Workstation's default zone accepts inbound `1025-65535/tcp`, so any hostNetwork service binding a high port would be LAN-reachable unless explicitly fenced. Decision (2026-08-26): each such service gets a **pair** of permanent rich rules — tailnet-source accept at `priority=-1`, protocol/port catch-drop at `priority=0`. Applied for 8080 alongside 6443's source-scoped accept; repeat the pair for every future hostNetwork port. Post-install gate: `curl http://<node-LAN-IP>:<port>/healthz` must refuse while the tailnet path answers.

## Images must enter the cluster store

k3s embeds its own containerd; Docker-built images are invisible to pods. Path: `docker save <img> | mlops-sudo image-import` (helper subcommand), then deploy with explicit `pullPolicy: IfNotPresent` — `:latest` defaults to `Always` and defeats node-local images.

## Chart conventions (owned services)

One chart per module, no umbrella. Values files carry only non-secret config; credentials arrive via `envSecretRef` → pre-created Secret (created on-box from the box `.env`, never through tracked files or chat). Job charts take a jar source at install time: `jar.existingClaim` (PVC — preferred; SELinux denies pod reads of home-dir hostPaths) or `jar.hostPath` fallback. The init container stages the jar into pod-local `emptyDir` before start — PVC bind-mounts proved unstable for sustained jar random-access on this node (mid-run `NoClassDefFoundError`). Template guards refuse empty or ambiguous sources.

Probe semantics: the gateway's `/healthz` is process-liveness only — it does not gate on Kafka reachability. Job charts instead liveness-probe **checkpoint freshness** (exec `find <dir> -mmin -2`), restoring the healthcheck parity the retired docker-run containers had.

Packaging note: the module Dockerfiles bake jars into self-contained job images (the registry path); charts currently bind-mount node-local jars instead — one of the two becomes canonical when the data-group migration lands. Kubernetes `$(VAR)` expansion does **not** word-split: multi-flag JVM options must be rendered as individual argv elements (charts do), never passed as one quoted string.
