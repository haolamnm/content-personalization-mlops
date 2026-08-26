---
title: "Operations Design — Kubernetes, Scale, Security, and Observability"
id: architecture-operations
date: 2026-08-26
type: architecture
status: draft
tags: [architecture, kubernetes, operations, observability]
related:
  - ./system-flow.md
  - ./production-bar.md
  - ./decision-gates.md
  - ../../adr/0003-ram-budgeted-local-infrastructure.md
  - ../../adr/0007-kubernetes-adoption-k3s-helm.md
---

# Operations Design — Kubernetes, Scale, Security, and Observability

This page answers one question: how does the platform remain operable as services, traffic, and failure modes grow?

## Runtime and delivery

Compose remains the RAM-budgeted development venue. k3s and Helm are the target deployment surface after the Phase 1 boundary; Strimzi and CloudNativePG are candidates for stateful Kafka and PostgreSQL lifecycle management.

Argo CD and Flux are GitOps alternatives. They become useful when manual Helm releases across environments create drift or deployment mistakes.

## Scaling

KEDA is a candidate autoscaler for workers driven by Kafka lag, RabbitMQ queue depth, or other event-source metrics. It is especially interesting after the RabbitMQ experiment because the same command lane can demonstrate backlog-aware scaling.

KEDA must not compensate for a bad consumer design. Partition counts, idempotency, concurrency limits, and downstream capacity still define the safe scaling boundary.

## Security and identity

Keycloak is a candidate self-hosted OIDC provider for identity, login, and tenant boundaries. A managed identity provider is an alternative when self-hosting is not the learning goal.

Local `.env` configuration is acceptable for the learning venue. Shared or production deployments need a secret-management boundary, such as Kubernetes Secrets integrated with an external secret manager.

## Observability

OpenTelemetry instruments the request and data paths. SigNoz is the current observability target, with Prometheus and Grafana for metrics and dashboards.

Loki, Tempo, and Jaeger are specialized alternatives for logs and traces. Alertmanager is a candidate for routing actionable alerts. Vector or ELK remains a candidate log pipeline.

## Analytics and performance

Superset is the product and platform analytics surface. Trino supplies the lakehouse query path when Superset cannot query Iceberg directly.

k6, Locust, and Gatling are hardening tools for repeatable throughput, latency, and failure tests. They are not runtime services in the recommendation path.

## Operational rule

Every operational addition needs a signal, a failure mode, an owner, and a rollback or teardown path. The local machine continues to run one profile group at a time.

## Read next

- [Data platform](./data-platform.md) for stateful infrastructure.
- [Production bar](./production-bar.md) for operational proof.
- [Decision gates](./decision-gates.md) for introducing platform operators and controllers.

## Primary references

- [KEDA scalers](https://keda.sh/docs/2.20/scalers/)
- [KServe administration](https://kserve.github.io/website/docs/admin-guide/overview)
