---
title: "Flink Streaming"
id: agents-knowledge-flink-streaming
date: 2026-08-25
type: knowledge
status: active
tags: [flink, streaming, watermarks, checkpoints]
related:
  - ../knowledge/image-pins.md
  - ../../../platform/streaming/event-counts/README.md
  - ../../../.agents/rules/java-streaming-correctness.md
---

# Flink Streaming

Operational knowledge from the first job (`platform/streaming/event-counts`); module README carries the binding knobs.

## Embedded runtime constraint

`LocalStreamEnvironment` at parallelism>1 never fires event-time windows on Flink 2.2.1 — records arrive, upstream watermarks emit, timers never trigger (reproduced in-process; disabled repro test ships with the module). Embedded runs pin parallelism 1. Real clusters are unaffected; scaling out belongs to the deployment-shape ADR.

## Watermarks

Punctuated per-record emission (running max − bound) over periodic emitters: deterministic in tests, identical behavior on clusters. Strategy split: core bounded-punctuated generator is unit-tested pure; the `withIdleness` wrapper is deployment assembly — **the idleness wrapper misbehaves in fast finite batches even at parallelism 1** (channels go idle between records), so batch-style tests must use the core strategy. Idleness still required on real clusters so silent partitions can't pin the merged watermark.

## Dependency traps (each cost real debugging time)

- `flink-connector-base` arrives provided-scoped transitively via the connector (cluster-provides assumption); embedded fat jars must declare it compile-scope explicitly or runtime dies on `RecordEmitter` CNFE.
- Flink bundles slf4j-api **1.7.x** → logging needs `log4j-slf4j-impl`; the SLF4J-2.x provider silently NOPs everything.
- Checkpoint storage moved to config options: `CheckpointingOptions.CHECKPOINT_STORAGE="filesystem"` (backend *type*) + `CHECKPOINTS_DIRECTORY=<uri>` — putting the URI in the type slot throws CNFE from the storage loader.
- Kafka connector 5.x commits offsets on checkpoints automatically; the old builder knob is gone.
- Sink V2 writers implement `write/flush/close` — no `prepareCommit`; `SinkFunction` is removed entirely.
- JDK 25 runs Flink fine with `--add-opens` for java.base packages (lang/util/io/net/nio + sun.nio.ch); same set goes in surefire argLine.
