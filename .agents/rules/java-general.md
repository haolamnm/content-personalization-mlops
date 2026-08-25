---
description: General Java rules for the Flink job and Kafka Streams enrichment service — umbrella entry; specifics live in java-*.md siblings
globs: ["**/*.java", "**/pom.xml"]
alwaysApply: false
---

# Java General Rules

Java owns stream processing ([ADR 0004](../../docs/adr/0004-polyglot-language-per-concern.md)): the Flink job plus one Kafka Streams enrichment service. Umbrella entry — read the sibling matching your change:

| Sibling | Covers |
|:---|:---|
| [`java-streaming-correctness.md`](./java-streaming-correctness.md) | Event time, watermarks, state TTL, checkpoints, idempotent sinks |
| [`java-build-and-testing.md`](./java-build-and-testing.md) | Maven modules, shade fat jars, version pinning, MiniCluster tests |

## Universal Constraints

- **Records for data, sealed interfaces for closed hierarchies**: event models are immutable records; no JavaBean setters on domain types.
- **JVM memory is budgeted** ([`resource-budget`](./resource-budget.md)): heap sizes set explicitly per service in compose, never defaults; a JVM that grows past its allocation is a defect.
- **No Lombok/magic**: explicit code over annotation-generated code — this codebase teaches, so it stays readable.
- JDK 25 LTS from `.computers/MACBOOK.md`; Maven 3.9.x; both pinned per-module in `pom.xml` where relevant.
- `mvn -q package` green + tests passing before delivery (`verify-before-done` gate).
