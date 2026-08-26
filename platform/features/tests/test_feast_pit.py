import runpy
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from mlops_features.snapshot import write_feature_sources


def test_feast_historical_retrieval_is_point_in_time_correct(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "feature_repo"
    repo.mkdir()
    _ = (repo / "feature_store.yaml").write_text(
        "project: content_personalization\n"
        + "registry: data/registry.db\n"
        + "provider: local\n"
        + "offline_store:\n"
        + "  type: dask\n"
        + "online_store:\n"
        + "  type: sqlite\n"
        + "  path: data/online_store.db\n"
        + "entity_key_serialization_version: 3\n"
    )
    definitions_path = Path(__file__).parents[1] / "feature_repo" / "feature_definitions.py"
    _ = (repo / "feature_definitions.py").write_text(definitions_path.read_text())
    (repo / "data").mkdir()
    monkeypatch.chdir(repo)

    events = pd.DataFrame(
        [
            {
                "user_id": "u1",
                "item_id": "i1",
                "event_type": "click",
                "created_at": "2026-01-01T00:00:00Z",
                "ingested_at": "2026-01-01T00:05:00Z",
            },
            {
                "user_id": "u2",
                "item_id": "i2",
                "event_type": "impression",
                "created_at": "2026-01-01T01:00:00Z",
                "ingested_at": "2026-01-01T01:00:01Z",
            },
            {
                "user_id": "u1",
                "item_id": "i1",
                "event_type": "impression",
                "created_at": "2026-01-01T02:00:00Z",
                "ingested_at": "2026-01-01T02:00:01Z",
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
    entity_df = pd.DataFrame(
        [
            {
                "user_id": "u1",
                "item_id": "i2",
                "event_timestamp": datetime(2026, 1, 2, tzinfo=UTC),
                "label": 1,
            },
        ]
    )

    result = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "user_interaction_features:user_click_count_7d",
            "item_interaction_features:item_click_count_7d",
        ],
    ).to_df()

    assert list(result["user_click_count_7d"]) == [1]
    assert list(result["item_click_count_7d"]) == [0]
    assert list(result["label"]) == [1]

    available_result = store.get_historical_features(
        entity_df=pd.DataFrame(
            [
                {
                    "user_id": "u1",
                    "item_id": "i1",
                    "event_timestamp": datetime(2026, 1, 1, 0, 5, tzinfo=UTC),
                }
            ]
        ),
        features=[
            "user_interaction_features:user_click_count_7d",
            "item_interaction_features:item_click_count_7d",
        ],
    ).to_df()

    assert list(available_result["user_click_count_7d"]) == [1]
    assert list(available_result["item_click_count_7d"]) == [1]
