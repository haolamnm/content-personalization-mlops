from pathlib import Path
from typing import cast

import pytest

from mlops_features.materialize import feature_repo_path, feature_store_for_repo


def test_materializer_can_target_runtime_redis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _ = (tmp_path / "feature_store.yaml").write_text(
        "project: content_personalization\n"
        + "registry: data/registry.db\n"
        + "provider: local\n"
        + "offline_store:\n"
        + "  type: dask\n"
        + "online_store:\n"
        + "  type: redis\n"
        + '  connection_string: "localhost:6379"\n'
        + "entity_key_serialization_version: 3\n"
    )
    monkeypatch.setenv("FEATURE_REDIS_URL", "redis.internal:6379,password=secret")

    store = feature_store_for_repo(tmp_path)

    online_config = cast(dict[str, object], store.config.online_config)
    assert online_config["connection_string"] == "redis.internal:6379,password=secret"


def test_materializer_uses_redis_password_for_the_local_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _ = (tmp_path / "feature_store.yaml").write_text(
        "project: content_personalization\n"
        + "registry: data/registry.db\n"
        + "provider: local\n"
        + "offline_store:\n"
        + "  type: dask\n"
        + "online_store:\n"
        + "  type: redis\n"
        + '  connection_string: "localhost:6379"\n'
        + "entity_key_serialization_version: 3\n"
    )
    monkeypatch.delenv("FEATURE_REDIS_URL", raising=False)
    monkeypatch.setenv("REDIS_PASSWORD", "local-secret")

    store = feature_store_for_repo(tmp_path)

    online_config = cast(dict[str, object], store.config.online_config)
    assert online_config["connection_string"] == "localhost:6379,password=local-secret"


def test_materializer_accepts_explicit_repo_path_for_installed_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEATURE_REPO_PATH", str(tmp_path))

    assert feature_repo_path() == tmp_path
