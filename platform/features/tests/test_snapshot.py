import pandas as pd
import pytest

from mlops_features.snapshot import build_feature_snapshot


def _event(
    user_id: str,
    item_id: str,
    event_type: str,
    created_at: str,
    ingested_at: str,
) -> dict[str, str]:
    return {
        "user_id": user_id,
        "item_id": item_id,
        "event_type": event_type,
        "created_at": created_at,
        "ingested_at": ingested_at,
    }


def test_snapshot_excludes_current_event_and_preserves_entity_time() -> None:
    events = pd.DataFrame(
        [
            _event("u1", "i1", "click", "2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z"),
            _event("u1", "i1", "impression", "2026-01-02T00:00:00Z", "2026-01-02T00:00:01Z"),
        ]
    )

    snapshot = build_feature_snapshot(events)
    event_rows = snapshot.loc[snapshot["event_timestamp"] < snapshot["created_timestamp"]]

    assert event_rows.iloc[0]["user_click_count_7d"] == 0
    assert event_rows.iloc[1]["user_event_count_7d"] == 1
    assert event_rows.iloc[1]["user_click_count_7d"] == 1
    assert event_rows.iloc[1]["item_event_count_7d"] == 1
    assert event_rows.iloc[1]["event_timestamp"] == pd.Timestamp("2026-01-02", tz="UTC")


def test_snapshot_expires_events_at_seven_day_boundary() -> None:
    events = pd.DataFrame(
        [
            _event("u1", "i1", "click", "2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z"),
            _event("u1", "i1", "impression", "2026-01-08T00:00:00Z", "2026-01-08T00:00:01Z"),
        ]
    )

    snapshot = build_feature_snapshot(events)
    event_time = snapshot.loc[
        snapshot["event_timestamp"] == pd.Timestamp("2026-01-08T00:00:00Z")
    ].iloc[0]

    assert event_time["user_event_count_7d"] == 0
    assert event_time["item_click_count_7d"] == 0


def test_snapshot_scores_equal_timestamps_before_updating_history() -> None:
    events = pd.DataFrame(
        [
            _event("u1", "i1", "click", "2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z"),
            _event("u1", "i1", "impression", "2026-01-01T00:00:00Z", "2026-01-01T00:00:02Z"),
            _event("u1", "i1", "impression", "2026-01-01T01:00:00Z", "2026-01-01T01:00:01Z"),
        ]
    )

    snapshot = build_feature_snapshot(events)
    event_rows = snapshot.loc[snapshot["event_timestamp"] < snapshot["created_timestamp"]]

    assert list(event_rows["user_event_count_7d"]) == [0, 0, 2]
    assert list(event_rows["user_click_count_7d"]) == [0, 0, 1]


def test_snapshot_does_not_use_late_events_before_their_ingestion_time() -> None:
    events = pd.DataFrame(
        [
            _event("u1", "i1", "click", "2026-01-01T10:00:00Z", "2026-01-01T10:05:00Z"),
            _event("u1", "i1", "impression", "2026-01-01T10:02:00Z", "2026-01-01T10:02:01Z"),
            _event("u1", "i1", "impression", "2026-01-01T10:06:00Z", "2026-01-01T10:06:01Z"),
        ]
    )

    snapshot = build_feature_snapshot(events)
    first_event = snapshot.loc[
        snapshot["event_timestamp"] == pd.Timestamp("2026-01-01T10:02:00Z")
    ].iloc[0]
    third_event = snapshot.loc[
        snapshot["event_timestamp"] == pd.Timestamp("2026-01-01T10:06:00Z")
    ].iloc[0]

    assert first_event["user_click_count_7d"] == 0
    assert third_event["user_click_count_7d"] == 1


def test_snapshot_emits_post_ingestion_state_for_a_delayed_event() -> None:
    events = pd.DataFrame(
        [
            _event("u1", "i1", "click", "2026-01-01T10:00:00Z", "2026-01-01T10:05:00Z"),
        ]
    )

    snapshot = build_feature_snapshot(events)
    available = snapshot.loc[snapshot["event_timestamp"] == pd.Timestamp("2026-01-01T10:05:00Z")]

    assert len(available) == 1
    assert available.iloc[0]["user_event_count_7d"] == 1
    assert available.iloc[0]["user_click_count_7d"] == 1
    assert available.iloc[0]["item_event_count_7d"] == 1
    assert available.iloc[0]["item_click_count_7d"] == 1


def test_snapshot_emits_post_ingestion_state_for_equal_persisted_timestamps() -> None:
    events = pd.DataFrame(
        [
            _event("u1", "i1", "click", "2026-01-01T10:00:00Z", "2026-01-01T10:00:00Z"),
        ]
    )

    snapshot = build_feature_snapshot(events)

    assert len(snapshot) == 2
    assert list(snapshot["user_event_count_7d"]) == [0, 1]
    assert list(snapshot["user_click_count_7d"]) == [0, 1]


def test_snapshot_rolling_counts_expire_each_event_independently() -> None:
    events = pd.DataFrame(
        [
            _event("u1", "i1", "click", "2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z"),
            _event("u1", "i1", "impression", "2026-01-01T00:00:01Z", "2026-01-01T00:00:02Z"),
            _event("u1", "i1", "impression", "2026-01-08T00:00:01Z", "2026-01-08T00:00:02Z"),
        ]
    )

    snapshot = build_feature_snapshot(events)
    event_time = snapshot.loc[
        snapshot["event_timestamp"] == pd.Timestamp("2026-01-08T00:00:01Z")
    ].iloc[0]

    assert event_time["user_event_count_7d"] == 0
    assert event_time["user_click_count_7d"] == 0


def test_snapshot_requires_canonical_lake_columns() -> None:
    with pytest.raises(ValueError, match="events missing required columns"):
        _ = build_feature_snapshot(pd.DataFrame({"user_id": ["u1"]}))
