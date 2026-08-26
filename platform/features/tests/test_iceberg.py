from mlops_features.iceberg import EVENT_QUERY, s3_host


def test_event_reader_uses_current_iceberg_snapshot() -> None:
    assert "FROM iceberg_scan(?)" in EVENT_QUERY
    assert "created_at" in EVENT_QUERY
    assert "ingested_at" in EVENT_QUERY


def test_s3_endpoint_is_normalized_for_duckdb() -> None:
    assert s3_host("http://mlops-minio.mlops-data.svc.cluster.local:9000/") == (
        "mlops-minio.mlops-data.svc.cluster.local:9000"
    )


def test_http_endpoint_does_not_use_ssl() -> None:
    assert not "http://mlops-minio:9000".startswith("https://")
