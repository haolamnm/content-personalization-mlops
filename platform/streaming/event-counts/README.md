# Event Counts — first Flink job

Consumes `mlops.events.raw`, counts events per `event_type` in **10s event-time tumbling windows**, prints window results to stdout. Too-late events go to a side output (`TOO-LATE` print prefix) — never silently dropped ([streaming-correctness rule](../../../.agents/rules/java-streaming-correctness.md)).

## Resilience knobs (documented per rule)

| Knob | Value | Notes |
|:---|:---|:---|
| Checkpoint interval | 10 s | `enableCheckpointing(10_000)` |
| Consistency mode | EXACTLY_ONCE | set explicitly |
| Min pause between checkpoints | 5 s | |
| Checkpoint timeout | 60 s | |
| Tolerable checkpoint failures | 3 | then the job fails fast |
| Checkpoint storage | `file:///tmp/flink-checkpoints` | **dev-proof only** — durable state backend arrives with the deployment design |
| Starting offsets | `latest()` on cold start | a cold start (no checkpoint state) silently skips everything produced during downtime; checkpointed restarts resume exactly |

Watermarks: bounded-out-of-orderness **2 s** over gateway-stamped `created_at`; allowed lateness **5 s** beyond window end before an event is side-output as too late.

State profile: only window state exists (per `event_type` key — cardinality ≤ 5), cleaned automatically when windows purge; no unbounded keyed state, so no TTL is declared yet.

## Build & run

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@25/libexec/openjdk.jdk/Contents/Home   # Mac keg-only JDK
mvn -q package          # target/event-counts.jar — shaded fat jar
mvn -q test             # MiniCluster tests, deterministic, no brokers needed

# embedded run (LocalStreamEnvironment) against the mesh from inside the data network:
docker run --rm --network mlops-data \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  -v "$PWD/target/event-counts.jar:/app/event-counts.jar" \
  eclipse-temurin:25-jre java   # digest sha256:f9e65324a37f2 verified at adoption --add-opens=java.base/java.lang=ALL-UNNAMED \
    --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED \
    --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED \
    --add-opens=java.base/sun.nio.ch=ALL-UNNAMED -jar /app/event-counts.jar
```

JDK 25 needs those `--add-opens` flags at runtime (Pekko/Netty internals); tests get the same set via surefire argLine.

## Versions (pinned, matched pair)

Flink **2.2.1** + `flink-connector-kafka` **5.0.0-2.2** — connector releases track specific Flink minors and no `-2.3` build existed at adoption; Kafka clients ride transitively at 4.2.x, compatible with the compose-pinned broker 4.3.1. Connector 5.x commits offsets on checkpoints by design (the old builder knob is gone).

Tests use **punctuated per-record watermarks** because periodic emission (200 ms default) never fires inside a fast finite batch — production sources emit periodically; the pipeline code is identical either way.

## Known constraint: embedded runs are parallelism-1

`LocalStreamEnvironment` at parallelism>1 never fires event-time windows in Flink 2.2.1: records arrive at the window operator, upstream subtasks emit watermarks (verified by probes and REST metrics), yet no timer ever triggers — reproduced minimally in-process (`Parallel3ReproTest`, disabled). Real clusters don't use this runtime; the job therefore pins embedded runs to parallelism 1 (`-Dflink.parallelism=N` overrides for experiments), and the deployment-shape ADR owns scaling out. Related hardening kept regardless: punctuated per-record watermarks and `withIdleness(2s)` so idle Kafka partitions can't stall event time on a real cluster.

## Known deferrals

- Malformed-line rate metrics arrive with the observability phase; today they are filtered and counted nowhere.
- Real sink (Iceberg/MinIO) replaces stdout in the lakehouse slice; idempotent-write rule binds that work, not this job's stdout.
- Deployment shape (session cluster vs application mode) is a pending ADR — this job runs embedded until it lands.
