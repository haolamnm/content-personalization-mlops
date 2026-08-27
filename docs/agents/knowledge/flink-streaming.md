---
title: "Flink Streaming"
id: agents-knowledge-flink-streaming
date: 2026-08-25
type: knowledge
status: active
tags: [flink, streaming, watermarks, checkpoints]
related:
  - ../knowledge/image-pins.md
  - ../../../platform/streaming/event-counts/AGENTS.md
  - ../../../platform/streaming/events-lake/AGENTS.md
  - ../../adr/0008-iceberg-lake-sink-dual-pin.md
  - ../../../.agents/rules/java-streaming-correctness.md
---

# Flink Streaming

Operational knowledge from the streaming jobs (`platform/streaming/event-counts`, `platform/streaming/events-lake`); module AGENTS.md files carry the binding knobs.

## Version pins are per-module (dual pin)

The two jobs intentionally run different Flink majors: event-counts on **2.2.1**, events-lake on **2.1.3** — because `iceberg-flink-runtime` ships per-major jars and Iceberg 1.11.0 has no `-2.2` build yet ([ADR 0008](../../adr/0008-iceberg-lake-sink-dual-pin.md)). Separate containers share no classpath, so this is safe. Collapse back to one version when Iceberg 1.12.0 lands; until then, connector bumps must be checked per module against their own major.

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
- Iceberg's flink runtime assumes `flink-table-common`, `flink-table-runtime`, and hadoop are **provided**; embedded fat jars declare all three compile-scope. Hadoop-common drags `slf4j-reload4j`/`log4j` in — exclude them or the second SLF4J binding hijacks logging.
- Shading hadoop-common also merges dnsjava's service entry whose classes live only under `META-INF/versions/18/` — the shade manifest must set `Multi-Release: true` or JDK startup dies with `ServiceConfigurationError: InetAddressResolverProvider`.
- RowData/TimestampData live in `flink-table-common`; internal timestamp representation is millisecond + nano-of-milli — use `TimestampData.fromInstant(...)` / `.toInstant()` for lossless round-trips; `fromEpochMillis` silently truncates sub-millisecond precision.

## THINKBOOK build boundary

The THINKBOOK host is not a supported Maven build environment: it has JDK 21 and no host Maven, while the jobs require JDK 25. The shade-defect investigation was closed on 2026-08-26 by building and testing both modules in `maven:3.9-eclipse-temurin-25`; `mvn -q package` and `mvn -q test` exited 0 for `event-counts` and `events-lake`, and no shaded-class failure reproduced. Use the pinned Maven container for box builds; do not diagnose a host-toolchain mismatch as a jar shade defect.
