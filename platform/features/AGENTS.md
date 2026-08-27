# Feature Platform

The Feature Platform owns the shared user/item feature contract between historical training and online ranking. It projects the canonical Iceberg event table into causally safe feature rows, registers those rows with Feast, and materializes the latest values into Redis.

## Seam

```text
Iceberg JDBC catalog + MinIO
        │ current snapshot
        ▼
FeatureSnapshotBuilder ──► data/user_interaction_features.parquet
                       └──► data/item_interaction_features.parquet
                                      │
                             Feast Redis materialization
                                      ▼
                             latest user/item values
```

The explicit adapter in `src/mlops_features/iceberg.py` resolves the current Iceberg metadata file from the existing JDBC catalog and reads it with DuckDB's Iceberg extension; the resulting Parquet projections are the Feast-compatible offline sources, queried by Feast's supported Dask offline store. This keeps Iceberg as the source of truth while keeping the catalog-to-feature projection under our control.

## Local verification

```bash
uv sync --directory platform/features --python 3.14
uv run --directory platform/features pytest -q
make features-lint
```

The PIT test uses SQLite only to isolate historical retrieval. The Redis test is an integration test and runs when `FEATURE_REDIS_URL` points to a reachable Redis instance. `make features-lint` runs Ruff, `ty`, and basedpyright against the package.

## Runtime materialization

Run from this directory after exporting the JDBC catalog and MinIO credentials:

```bash
ICEBERG_POSTGRES_DSN='postgresql://mlops:...@mlops-postgres-rw.mlops-data.svc.cluster.local:5432/mlops' \
ICEBERG_S3_ENDPOINT='http://mlops-minio.mlops-data.svc.cluster.local:9000' \
ICEBERG_S3_ACCESS_KEY='mlops-admin' \
ICEBERG_S3_SECRET_KEY='...' \
uv run feature-materialize
```

The runtime feature repository uses authenticated `localhost:6379` for local authoring. For k3s, run the materializer from a pod or box with cluster DNS and set `FEATURE_REDIS_URL="mlops-redis-master.mlops-data.svc.cluster.local:6379,password=$(kubectl get secret -n mlops-data redis-auth -o jsonpath='{.data.redis-password}' | base64 -d)"`; the credential comes from the Redis Secret and is never committed here.
For the Compose data group, export the same `REDIS_PASSWORD` used by Compose before running `uv run feature-materialize`; the materializer replaces the sample password in `feature_store.yaml` with that environment value. The checked-in sample default matches `.env.example` for a zero-configuration local run.
When installed from a wheel, pass the repository explicitly with `FEATURE_REPO_PATH=/path/to/feature_repo uv run feature-materialize`; the wheel contains the materializer, while the repository remains a writable runtime data directory for generated Parquet and registry files.
