---
title: "Data Platform Design — Sources, Contracts, and Lakehouse"
id: architecture-data-platform
date: 2026-08-26
type: architecture
status: draft
tags: [architecture, data, postgres, kafka, iceberg]
related:
  - ./system-flow.md
  - ./domain-contracts.md
  - ./messaging.md
  - ./decision-gates.md
---

# Data Platform Design — Sources, Contracts, and Lakehouse

This page answers one question: how does source data become governed, replayable, queryable platform data?

## Source and capture plane

PostgreSQL owns transactional users and interaction state. MongoDB owns document-shaped content metadata. Debezium and Kafka Connect publish database changes to Kafka topics.

The app event path and CDC path are separate contracts. An interaction event says what the user did; a CDC record says what changed in a database.

## PostgreSQL connection boundary

PgBouncer is a conditional pooler between application clients and PostgreSQL. It becomes useful when API processes, workers, training jobs, schedulers, and dashboards compete for a finite connection budget.

Start with session pooling for compatibility. Transaction pooling can improve reuse but changes session semantics; Debezium and other session-sensitive clients stay on a direct path until compatibility is tested.

The trigger is measured connection count, connection startup cost, or PostgreSQL saturation—not the existence of multiple services.

## Event contract plane

Apicurio Registry is a candidate registry for versioned Avro, JSON Schema, Protobuf, OpenAPI, and AsyncAPI artifacts. It becomes valuable when multiple producers and consumers need compatibility rules and a central contract catalog.

Kafka UI is a development tool for inspecting topics, partitions, offsets, consumer groups, and lag. It is useful for learning and debugging but is not a production data dependency.

## Lakehouse plane

MinIO provides S3-compatible objects. Iceberg provides table schemas, snapshots, partitions, and replayable history. The current design uses a PostgreSQL-backed JDBC catalog to avoid introducing a catalog service too early.

Trino is the candidate query engine between Iceberg and users or tools such as Superset. dbt is a candidate SQL transformation layer for tested bronze, silver, and gold models.

LakeFS is a candidate for Git-like data branches and commits. Apache Polaris and Project Nessie are candidates when the Iceberg catalog needs a service boundary across multiple engines or environments.

## Quality and lineage

Great Expectations and Soda are alternative data-quality approaches. OpenLineage defines standard dataset, job, and run metadata; Marquez is a candidate backend/UI for that lineage.

These tools become more valuable when a bad dataset, missing partition, feature mismatch, or unexplained transformation has a real cost.

## Design constraints

- Raw landing preserves producer output before enrichment or aggregation.
- Event time and processing time remain distinct in streaming contracts.
- Schema evolution is explicit; incompatible changes fail at a boundary instead of silently corrupting consumers.
- Query engines and catalog services are not added merely because Iceberg exists.
- Data quality and lineage claims require an executable check or a recorded lineage event.

## Read next

- [Messaging](./messaging.md) for Kafka and command transport.
- [Domain contracts](./domain-contracts.md) for event and table vocabulary.
- [Production bar](./production-bar.md) for replay and data-quality proof.

## Primary references

- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [Apicurio Registry](https://www.apicur.io/registry-v2/)
- [PgBouncer configuration](https://www.pgbouncer.org/config)
- [OpenLineage documentation](https://openlineage.io/docs/)
