---
title: "Production Bar — Evidence and Failure Behavior"
id: architecture-production-bar
date: 2026-08-26
type: standard
status: active
tags: [architecture, reliability, quality, verification]
related:
  - ./north-star.md
  - ./domain-contracts.md
  - ./decision-gates.md
---

# Production Bar — Evidence and Failure Behavior

This page answers one question: what must be proven before the platform can be called production-grade?

## End-to-end proof

- An interaction travels from the app to Kafka, through stream processing, into Iceberg, and into analytics.
- A recommendation request retrieves candidates, joins online features, scores them, and returns a response within a measured latency budget.
- Offline training is point-in-time correct and online/offline feature definitions stay aligned.
- A model is trained, tracked, versioned, evaluated, promoted, served, and measured against new outcomes.
- Kafka and Iceberg support replay, rebuild, backfill, and downstream consumer recovery.

## Failure proof

- Malformed, late, duplicate, and out-of-order events have explicit behavior.
- A worker crash before acknowledgement does not silently lose a command.
- Retries cannot create an unbounded poison-message loop.
- A model or feature failure has a safe fallback and an observable error signal.
- Connection exhaustion, consumer lag, feature staleness, and model drift are measurable.
- Rollback and replay procedures are documented and tested against disposable data.

## Operational proof

- Every service exposes a meaningful health or readiness signal.
- Traces connect the feed request to retrieval, model serving, and event emission.
- Metrics cover latency, throughput, lag, freshness, errors, and resource use.
- Logs are structured enough to correlate a request, event, job, model, or workflow.
- Deployment can move from Compose to Kubernetes without changing domain contracts.

## Learning proof

Every new platform tool must have a small experiment, a baseline, a measured result, and a written verdict. A tool is not adopted merely because it is popular or appears in a reference architecture.

## Read next

- [Service radar](./service-radar.md) for candidate tools.
- [Decision gates](./decision-gates.md) for adoption criteria.
