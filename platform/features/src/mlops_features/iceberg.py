"""Read the current Iceberg event snapshot through the existing JDBC catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import duckdb
import pandas as pd
import psycopg

EVENT_QUERY = """
SELECT user_id, item_id, event_type, created_at, ingested_at
FROM iceberg_scan(?)
"""


@dataclass(frozen=True)
class IcebergConfig:
    """Connection settings for the existing Postgres catalog and MinIO warehouse."""

    postgres_dsn: str
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str


def current_metadata_location(postgres_dsn: str) -> str:
    """Return the current metadata file for the canonical raw-event table."""
    with psycopg.connect(postgres_dsn) as connection:
        row = connection.execute(
            """
            SELECT metadata_location
            FROM iceberg_tables
            WHERE table_namespace = %s AND table_name = %s
            """,
            ("mlops_lake", "events_raw"),
        ).fetchone()
    if row is None:
        raise LookupError("Iceberg table mlops_lake.events_raw is not registered")
    return cast(str, row[0])


def read_current_events(config: IcebergConfig) -> pd.DataFrame:
    """Read the current Iceberg table snapshot as the canonical event frame."""
    metadata_location = current_metadata_location(config.postgres_dsn)
    connection = duckdb.connect()
    try:
        _ = connection.execute("INSTALL httpfs")
        _ = connection.execute("LOAD httpfs")
        _ = connection.execute("INSTALL iceberg")
        _ = connection.execute("LOAD iceberg")
        _ = connection.execute("SET s3_endpoint = ?", (s3_host(config.s3_endpoint),))
        _ = connection.execute("SET s3_use_ssl = ?", (config.s3_endpoint.startswith("https://"),))
        _ = connection.execute("SET s3_url_style = 'path'")
        _ = connection.execute("SET s3_access_key_id = ?", (config.s3_access_key,))
        _ = connection.execute("SET s3_secret_access_key = ?", (config.s3_secret_key,))
        return connection.execute(EVENT_QUERY, (metadata_location,)).fetchdf()
    finally:
        connection.close()


def s3_host(endpoint: str) -> str:
    return endpoint.removeprefix("http://").removeprefix("https://").rstrip("/")
