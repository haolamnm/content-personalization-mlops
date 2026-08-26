---
title: "Decision Gates — From Candidate to ADR"
id: architecture-decision-gates
date: 2026-08-26
type: standard
status: active
tags: [architecture, decisions, evidence, adr]
related:
  - ./service-radar.md
  - ./production-bar.md
  - ../../adr/index.json
---

# Decision Gates — From Candidate to ADR

This page answers one question: what evidence earns a candidate a binding architectural decision?

## Gate sequence

1. State the capability and owning bounded context.
2. Define the public seam: API, topic, queue, schema, table, or workflow contract.
3. Build the smallest representative slice.
4. Measure the relevant behavior: latency, throughput, memory, recovery, correctness, or operator effort.
5. Record the baseline, result, failure cases, and rejected alternatives.
6. Update the relevant architecture page and context map.
7. Write an ADR only when the choice is binding, alternatives were weighed, and a future change would be expensive or dangerous.

## Candidate gates

| Candidate | Evidence required before ADR |
|:---|:---|
| RabbitMQ | Worker crash, acknowledgement, retry, dead-letter, prefetch, and idempotency behavior compared with Kafka commands or another queue |
| Temporal versus Dagster | Representative training workflow compared by retries, state recovery, dependencies, schedules, and ownership |
| PgBouncer | Measured connection pressure and compatibility test for each client class; direct CDC path preserved |
| Apicurio Registry | Multiple producer/consumer schema evolution or a reproduced compatibility failure |
| Trino | Superset, Feast, or debugging needs a query engine beyond the current Iceberg access path |
| LakeFS, Nessie, or Polaris | Reproducible data branches or multi-engine catalog coordination is required |
| dbt | SQL transformations need tests, documentation, lineage, and repeatable runs beyond current jobs |
| Great Expectations or Soda | A real data-quality failure justifies a reusable validation framework |
| OpenLineage + Marquez | A real lineage question cannot be answered from existing job and table metadata |
| Evidently | A deployed model needs drift, data-quality, or prediction-quality monitoring |
| KServe, BentoML, or Triton | Ray Serve no longer covers the required model runtime, rollout, scaling, or protocol |
| KEDA | Worker scaling must respond to Kafka lag or RabbitMQ backlog on Kubernetes |
| Keycloak or managed OIDC | The product crosses from synthetic/single-user operation into real multi-user or multi-tenant operation |
| Argo CD or Flux | Manual delivery creates demonstrated configuration drift or release errors |

## Anti-sprawl rule

A name in the service radar is not an adoption commitment. Mutually exclusive alternatives stay documented until one wins a measured comparison; conditional services stay out of the running stack until their trigger occurs.

## ADR boundary

The architecture section is exploratory and context-routable. The ADR section is binding history. Never hide an unresolved candidate in an ADR just to make the architecture look finished.

## Read next

- [Service radar](./service-radar.md) for the complete candidate map.
- [Production bar](./production-bar.md) for evidence standards.
