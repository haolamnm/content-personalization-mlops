---
description: Streaming correctness for the Flink job and Kafka Streams service — event time, watermarks, state, checkpoints
globs: ["**/*.java", "**/*.flink", "**/pom.xml"]
alwaysApply: false
---

# Rule: Java Streaming Correctness

## Constraints

- **Event time, always**: windowing and joins run on event time with watermarks; processing-time windows are banned unless the decision log records why.
- **Idempotent or transactional sinks only**: lakehouse/serving writes survive replays — a replayed checkpoint must not duplicate rows (upserts, Iceberg equality deletes, or exactly-once producer semantics).
- **State has a TTL**: every keyed state declares a retention/TTL; unbounded state that grows with user/item cardinality is a defect waiting for OOM ([`resource-budget`](./resource-budget.md)).
- **Checkpointing is configured before the first run**: interval + tolerance documented in the job's module README; jobs start in exactly-once mode.
- **Serialization is explicit**: POJO/Avro schemas registered and versioned; adding a field is backward-compatible by default, breaking changes need a topic/schema-version bump recorded in the module CONTEXT.md and relevant knowledge note.
- Late data is handled on purpose: allowed-lateness plus a side output for too-late events — silently dropped events are banned.
