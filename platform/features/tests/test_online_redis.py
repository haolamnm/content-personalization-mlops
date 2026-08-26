import os
import runpy
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from mlops_features.snapshot import write_feature_sources

pytestmark = pytest.mark.integration


def test_materialized_feature_service_matches_offline_definition(tmp_path: Path) -> None:
    redis_connection = os.getenv("FEATURE_REDIS_URL")
    if not redis_connection:
        raise pytest.skip.Exception("FEATURE_REDIS_URL is not set")

    repo = tmp_path / "feature_repo"
    repo.mkdir()
    (repo / "data").mkdir()
    _ = (repo / "feature_store.yaml").write_text(
        "project: content_personalization\n"
        + "registry: data/registry.db\n"
        + "provider: local\n"
        + "offline_store:\n"
        + "  type: dask\n"
        + "online_store:\n"
        + "  type: redis\n"
        + f"  connection_string: {redis_connection!r}\n"
        + "  key_ttl_seconds: 604800\n"
        + "entity_key_serialization_version: 3\n"
    )
    definitions_path = Path(__file__).parents[1] / "feature_repo" / "feature_definitions.py"
    _ = (repo / "feature_definitions.py").write_text(definitions_path.read_text())
    now = datetime.now(UTC).replace(microsecond=0)
    events = pd.DataFrame(
        [
            {
                "user_id": "redis-user",
                "item_id": "redis-item",
                "event_type": "click",
                "created_at": (now - timedelta(days=1)).isoformat(),
                "ingested_at": (now - timedelta(days=1) + timedelta(seconds=1)).isoformat(),
            },
            {
                "user_id": "redis-user",
                "item_id": "redis-item",
                "event_type": "impression",
                "created_at": now.isoformat(),
                "ingested_at": (now + timedelta(seconds=1)).isoformat(),
            },
        ]
    )
    _ = write_feature_sources(events, repo / "data")

    objects = runpy.run_path(str(repo / "feature_definitions.py"))
    from feast import FeatureStore

    store = FeatureStore(repo_path=str(repo))
    store.apply(
        [
            objects["user"],
            objects["item"],
            objects["user_interaction_features"],
            objects["item_interaction_features"],
        ]
    )
    store.materialize(start_date=now - timedelta(days=7), end_date=now + timedelta(seconds=1))

    user_result = store.get_online_features(
        features=["user_interaction_features:user_click_count_7d"],
        entity_rows=[{"user_id": "redis-user", "item_id": "unseen-item"}],
    ).to_dict()
    item_result = store.get_online_features(
        features=["item_interaction_features:item_click_count_7d"],
        entity_rows=[{"user_id": "unseen-user", "item_id": "redis-item"}],
    ).to_dict()

    assert user_result["user_click_count_7d"] == [1]
    assert item_result["item_click_count_7d"] == [1]
