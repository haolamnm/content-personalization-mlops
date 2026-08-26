from pathlib import Path


def test_feature_repo_declares_shared_offline_and_online_service() -> None:
    definitions = Path(__file__).parents[1] / "feature_repo" / "feature_definitions.py"
    source = definitions.read_text()

    assert "FeatureService(" in source
    assert "FeatureView(" in source
    assert 'name="user_interaction_features_source"' in source
    assert 'name="item_interaction_features_source"' in source
    assert 'path="data/user_interaction_features.parquet"' in source
    assert 'path="data/item_interaction_features.parquet"' in source
    assert 'name="user_interaction_features"' in source
    assert 'name="item_interaction_features"' in source
    assert "online=True" in source


def test_feature_store_config_expires_redis_keys() -> None:
    config = Path(__file__).parents[1] / "feature_repo" / "feature_store.yaml"

    assert "key_ttl_seconds: 604800" in config.read_text()


def test_feature_store_config_has_authenticated_local_redis_default() -> None:
    config = Path(__file__).parents[1] / "feature_repo" / "feature_store.yaml"

    assert 'connection_string: "localhost:6379,password=change-me-8plus"' in config.read_text()
