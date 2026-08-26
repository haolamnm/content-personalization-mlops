---
title: "Service Radar — Architecture Routing Map"
id: architecture-service-radar
date: 2026-08-26
type: index
status: active
tags: [architecture, services, routing]
related:
  - ./index.json
  - ./north-star.md
  - ./decision-gates.md
---

# Service Radar — Architecture Routing Map

This page answers one question: which architecture page should I read before proposing a service?

## Current spine

| Service or context | Role | Status | Detail |
|:---|:---|:---|:---|
| PostgreSQL | Transactional source and Iceberg JDBC catalog | Implemented slice | [Data platform](./data-platform.md) |
| MongoDB | Content catalog source | Implemented/target source | [Data platform](./data-platform.md) |
| Debezium / Kafka Connect | Database-change capture | Implemented slice | [Data platform](./data-platform.md) |
| Kafka | Replayable event backbone | Implemented slice | [Messaging](./messaging.md) |
| Go event gateway | Interaction ingestion | Implemented slice | [System flow](./system-flow.md) |
| Flink / Kafka Streams | Event-time processing and enrichment | Implemented/target stream plane | [System flow](./system-flow.md) |
| MinIO / Iceberg | Durable object and table storage | Implemented slice | [Data platform](./data-platform.md) |
| Feast / Redis | Offline/online feature contract | Implemented slice | [ML platform](./ml-platform.md) |
| Ray / MLflow | Training and model lifecycle | Target | [ML platform](./ml-platform.md) |
| FastAPI / Ray Serve | Online model inference | Target | [ML platform](./ml-platform.md) |
| Rust retrieval / Go BFF / SvelteKit | Recommendation request path and product surface | Target | [System flow](./system-flow.md) |

## New names by question

| Question | First names to investigate | Read |
|:---|:---|:---|
| Need a command queue? | RabbitMQ, Celery, NATS JetStream | [Messaging](./messaging.md) |
| Need durable multi-step workflow state? | Temporal | [Messaging](./messaging.md) |
| Need data/ML asset orchestration? | Dagster, Airflow, Prefect | [ML platform](./ml-platform.md) |
| Need event/API schema governance? | Apicurio Registry | [Data platform](./data-platform.md) |
| Need to query Iceberg? | Trino | [Data platform](./data-platform.md) |
| Need SQL transformation? | dbt | [Data platform](./data-platform.md) |
| Need data versioning? | LakeFS, Nessie, Polaris | [Data platform](./data-platform.md) |
| Need lineage? | OpenLineage, Marquez | [Data platform](./data-platform.md) |
| Need model quality/drift? | Evidently | [ML platform](./ml-platform.md) |
| Need Kubernetes model serving? | KServe, BentoML, Triton | [ML platform](./ml-platform.md) |
| Need backlog-based worker scaling? | KEDA | [Operations](./operations.md) |
| Need identity? | Keycloak, managed OIDC | [Operations](./operations.md) |
| Need GitOps? | Argo CD, Flux | [Operations](./operations.md) |
| Need real-time OLAP? | ClickHouse, Pinot, Druid | [Data platform](./data-platform.md) |
| Need performance proof? | k6, Locust, Gatling | [Operations](./operations.md) |

## Classification

- **Core:** required by the end-to-end loop.
- **Conditional:** introduced when a measured workload or failure mode justifies it.
- **Experiment:** introduced to learn a distinct architectural pattern.
- **Alternative:** compared with an existing candidate, not installed alongside it by default.

## Read next

- [North star](./north-star.md) for the reason the platform exists.
- [Decision gates](./decision-gates.md) before adding or standardizing a name.
