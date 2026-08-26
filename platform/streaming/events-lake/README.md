# events-lake

Lands raw gateway events as an **Apache Iceberg table** (`mlops_lake.events_raw`) on MinIO — the lakehouse slice that closes Phase 1 ([ADR 0008](../../../docs/adr/0008-iceberg-lake-sink-dual-pin.md)).

## Shape

KafkaSource → parse → map to Flink internal rows → IcebergSink. No windows, no watermarks: the table is the raw landing zone; analytics reshape it downstream.

- Commits ride Flink checkpoints (**exactly-once**): every 10s checkpoint commits one Iceberg snapshot
- Malformed envelopes are filtered at parse; invalid-but-parseable events fail validation the same way
- Table bootstrap is idempotent: namespace and table are created on first run if missing
- Partitioned by `day(created_at)`; Parquet files target 128 MiB

## Dual pin (read this before bumping versions)

| Artifact | Version | Why |
|:---|:---|:---|
| Flink | 2.1.3 | iceberg-flink-runtime ships per-major jars; 1.11.0 has no `-2.2` build |
| flink-connector-kafka | 5.0.0-2.1 | same connector line as event-counts |
| iceberg-flink-runtime-2.1 / aws-bundle | 1.11.0 | official pair for Flink 2.1 |

event-counts stays on Flink 2.2.1 meanwhile. When Iceberg **1.12.0** ships with a `-2.2` runtime, bump both modules to one version in a single PR ([ADR 0008](../../../docs/adr/0008-iceberg-lake-sink-dual-pin.md) records the trigger).

## Config

| Env | Default | Meaning |
|:---|:---|:---|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:29094` | host-run dev default; mesh uses `kafka:9092` |
| `PG_JDBC_URL` | `jdbc:postgresql://localhost:5432/mlops` | catalog database |
| `PG_USER` / `PG_PASSWORD` | `mlops` / `mlops` | catalog credentials (from `.env`, never committed) |
| `LAKE_WAREHOUSE` | `s3://mlops-lake` | warehouse bucket |
| `MINIO_S3_ENDPOINT` | `http://localhost:9000` | S3-compatible endpoint override |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | `minioadmin` / `minioadmin` | MinIO credentials — reuse the compose `.env` values |

The bucket is **not** auto-created by the job; create it once per venue: `mc mb local/mlops-lake`.

## Run (embedded, like event-counts)

```bash
mvn -q package
# image pinned at adoption: eclipse-temurin:25-jre, digest sha256:f9e65324a37f2 verified
docker run -d --name flink-events-lake --network mlops-data \
  -v ~/.local/share/mlops/jars:/jars:ro \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  -e PG_JDBC_URL=jdbc:postgresql://postgres:5432/mlops \
  -e MINIO_S3_ENDPOINT=http://minio:9000 \
  --env-file .env \
  eclipse-temurin:25-jre java --add-opens=java.base/java.lang=ALL-UNNAMED \
    --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED \
    --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED \
    --add-opens=java.base/sun.nio.ch=ALL-UNNAMED \
    -jar /jars/events-lake.jar
```

Checkpoint storage is `/tmp/flink-checkpoints-lake` inside the container (separate from event-counts so both run concurrently).

**Cold-start caveat**: source starts at topic tail (`OffsetsInitializer.latest()`) and the container keeps checkpoints in ephemeral `/tmp` — every restart skips whatever was published while it was down. Same dev-tier tradeoff event-counts documents; durable state backend comes with the deployment-shape ADR. For a lake that claims to be a faithful record, prefer leaving this job running across experiments.

## Verify data landed

```bash
# catalog registration in Postgres (JDBC URI → psql needs postgresql:// form)
psql "$(echo "$PG_JDBC_URL" | sed 's/^jdbc://')" -U "$PG_USER" \
  -c "SELECT table_namespace, table_name FROM iceberg_tables WHERE table_namespace='mlops_lake';"
# Parquet files in MinIO — JDBC-catalog layout is {warehouse}/{namespace}/{table}/data/
mc ls --recursive local/mlops-lake/mlops_lake/events_raw/data/ | head
```

## Known constraints

- Same embedded parallelism>1 constraint as [event-counts](../event-counts/) — runs at parallelism 1 until a deployment-shape ADR exists
- Small files accumulate with dev commit cadence; compaction/maintenance is deliberately deferred (ADR 0008) — revisit when scans slow down
- The gateway server-stamps `created_at`, so partitions reflect gateway receipt time, not client event time

**Measured on THINKBOOK (2026-08-26)**: steady RSS ≈ 493 MiB; 9 posted events produced exactly 2 snapshots (`added-records` 5, then 4).
