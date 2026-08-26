"""Build the Feast source and materialize its latest values to Redis."""

from __future__ import annotations

import contextlib
import os
import runpy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import yaml
from feast import FeatureStore
from feast.repo_config import RepoConfig

from .iceberg import IcebergConfig, read_current_events
from .snapshot import write_feature_sources


def feature_store_for_repo(repo_path: Path) -> FeatureStore:
    """Load the repository and allow runtime environments to select Redis."""
    config = cast(dict[str, object], yaml.safe_load((repo_path / "feature_store.yaml").read_text()))
    redis_connection = os.getenv("FEATURE_REDIS_URL")
    if not redis_connection and (redis_password := os.getenv("REDIS_PASSWORD")):
        online_store = cast(dict[str, object], config["online_store"])
        connection_string = cast(str, online_store["connection_string"])
        connection_host = connection_string.split(",", maxsplit=1)[0]
        redis_connection = f"{connection_host},password={redis_password}"
    if redis_connection:
        online_store = cast(dict[str, object], config["online_store"])
        online_store["connection_string"] = redis_connection
    config["repo_path"] = repo_path
    return FeatureStore(config=RepoConfig(**config))


def feature_repo_path() -> Path:
    """Resolve the feature repository for source-checkout and installed runs."""
    configured_path = os.getenv("FEATURE_REPO_PATH")
    if configured_path:
        return Path(configured_path)
    source_checkout_path = Path(__file__).parents[2] / "feature_repo"
    if source_checkout_path.is_dir():
        return source_checkout_path
    raise FileNotFoundError(
        "feature repository not found; set FEATURE_REPO_PATH to a feature_repo directory"
    )


def materialize_latest(repo_path: Path) -> None:
    """Refresh the source projection, apply definitions, and materialize to Redis."""
    config = IcebergConfig(
        postgres_dsn=os.environ["ICEBERG_POSTGRES_DSN"],
        s3_endpoint=os.environ["ICEBERG_S3_ENDPOINT"],
        s3_access_key=os.environ["ICEBERG_S3_ACCESS_KEY"],
        s3_secret_key=os.environ["ICEBERG_S3_SECRET_KEY"],
    )
    _ = write_feature_sources(read_current_events(config), repo_path / "data")
    definitions = runpy.run_path(str(repo_path / "feature_definitions.py"))
    with contextlib.chdir(repo_path):
        store = feature_store_for_repo(repo_path)
        store.apply(
            [
                definitions["user"],
                definitions["item"],
                definitions["user_interaction_features"],
                definitions["item_interaction_features"],
                definitions["ranking_features"],
            ]
        )
        end_date = datetime.now(UTC)
        store.materialize(start_date=end_date - timedelta(days=7), end_date=end_date)


def main() -> None:
    materialize_latest(feature_repo_path())
