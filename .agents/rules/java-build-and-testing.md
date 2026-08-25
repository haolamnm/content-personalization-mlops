---
description: Maven build and testing conventions for Java services — fat jars, dependency discipline, Flink MiniCluster tests
globs: ["**/pom.xml", "**/*.java"]
alwaysApply: false
---

# Rule: Java Build & Testing

## Constraints

- **Maven, one module per service** ([ADR 0004](../../docs/adr/0004-polyglot-language-per-concern.md) consequences): `platform/streaming/<name>/pom.xml`; no multi-module reactor until a second artifact actually shares code.
- **Flink jobs ship as shade-plugin fat jars** with the documented `ServicesResourceTransformer` pattern; the jar builds clean via `mvn -q package` as part of [`verify-before-done`](./verify-before-done.md).
- **Versions pinned in pom.xml, never ranges**: Kafka/Flink clients match the compose-pinned broker/cluster versions of the active phase — drift between client and broker is a review-blocking defect.
- **Tests run on Flink MiniCluster / TopologyTestDriver** (Kafka Streams) — deterministic, no external brokers in unit scope; broker-backed integration tests are tagged and honor [`resource-budget`](./resource-budget.md).
- Snapshot dependencies and `-U` force-updates require a knowledge-note entry (`docs/agents/knowledge/`) or an ADR when architectural.
