"""Build point-in-time feature rows from the canonical Iceberg event shape."""

from __future__ import annotations

import heapq
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import cast

import pandas as pd

EVENT_COLUMNS = ("user_id", "item_id", "event_type", "created_at", "ingested_at")
FEATURE_COLUMNS = (
    "user_event_count_7d",
    "user_click_count_7d",
    "item_event_count_7d",
    "item_click_count_7d",
)
USER_FEATURE_COLUMNS = ("user_event_count_7d", "user_click_count_7d")
ITEM_FEATURE_COLUMNS = ("item_event_count_7d", "item_click_count_7d")
WINDOW = timedelta(days=7)


@dataclass(frozen=True)
class _Event:
    user_id: str
    item_id: str
    event_type: str
    created_at: pd.Timestamp
    ingested_at: pd.Timestamp


@dataclass
class _RollingCounts:
    entries: list[tuple[pd.Timestamp, int, str]]
    event_count: int = 0
    click_count: int = 0

    def add(self, timestamp: pd.Timestamp, event_type: str, sequence: int) -> None:
        heapq.heappush(self.entries, (timestamp, sequence, event_type))
        self.event_count += 1
        self.click_count += event_type == "click"

    def expire(self, cutoff: pd.Timestamp) -> None:
        while self.entries and self.entries[0][0] <= cutoff:
            _, _, event_type = heapq.heappop(self.entries)
            self.event_count -= 1
            self.click_count -= event_type == "click"


def build_feature_snapshot(events: pd.DataFrame) -> pd.DataFrame:
    """Return causally-safe user/item features at every event timestamp.

    Each output row describes the state immediately before its corresponding event. This
    strict-before rule means a training entity row at the event timestamp cannot see its own
    label-producing interaction.
    """
    missing = set(EVENT_COLUMNS) - set(events.columns)
    if missing:
        raise ValueError(f"events missing required columns: {sorted(missing)}")

    frame = events.loc[:, EVENT_COLUMNS].copy()
    frame["created_at"] = pd.to_datetime(frame["created_at"], utc=True)
    frame["ingested_at"] = pd.to_datetime(frame["ingested_at"], utc=True)
    frame = frame.sort_values(["created_at", "ingested_at"], kind="stable").reset_index(drop=True)

    records = [
        _Event(
            user_id=str(event.user_id),
            item_id=str(event.item_id),
            event_type=str(event.event_type),
            created_at=cast(pd.Timestamp, event.created_at),
            ingested_at=cast(pd.Timestamp, event.ingested_at),
        )
        for event in frame.itertuples(index=False)
    ]
    available_by_ingestion = sorted(
        enumerate(records), key=lambda indexed: (indexed[1].ingested_at, indexed[0])
    )
    pending: list[tuple[pd.Timestamp, pd.Timestamp, int, _Event]] = []
    user_history: dict[str, _RollingCounts] = defaultdict(lambda: _RollingCounts([]))
    item_history: dict[str, _RollingCounts] = defaultdict(lambda: _RollingCounts([]))
    rows: list[dict[str, object]] = []
    ingestion_index = 0

    for raw_timestamp, event_time_group in frame.groupby("created_at", sort=True):
        timestamp = cast(pd.Timestamp, raw_timestamp)
        while (
            ingestion_index < len(available_by_ingestion)
            and available_by_ingestion[ingestion_index][1].ingested_at <= timestamp
        ):
            sequence, event = available_by_ingestion[ingestion_index]
            heapq.heappush(
                pending,
                (event.created_at, event.ingested_at, sequence, event),
            )
            ingestion_index += 1

        cutoff = timestamp - WINDOW
        while pending and pending[0][0] < timestamp:
            _, _, sequence, event = heapq.heappop(pending)
            if event.created_at <= cutoff:
                continue
            user_history[event.user_id].add(event.created_at, event.event_type, sequence)
            item_history[event.item_id].add(event.created_at, event.event_type, sequence)

        for event in event_time_group.itertuples(index=False):
            user_id = str(event.user_id)
            item_id = str(event.item_id)
            user_events = user_history[user_id]
            item_events = item_history[item_id]
            user_events.expire(cutoff)
            item_events.expire(cutoff)
            rows.append(
                {
                    "user_id": user_id,
                    "item_id": item_id,
                    "event_timestamp": timestamp,
                    "created_timestamp": event.ingested_at,
                    "user_event_count_7d": user_events.event_count,
                    "user_click_count_7d": user_events.click_count,
                    "item_event_count_7d": item_events.event_count,
                    "item_click_count_7d": item_events.click_count,
                }
            )

    available_rows: list[dict[str, object]] = []
    available_user_history: dict[str, _RollingCounts] = defaultdict(lambda: _RollingCounts([]))
    available_item_history: dict[str, _RollingCounts] = defaultdict(lambda: _RollingCounts([]))
    ingestion_index = 0
    while ingestion_index < len(available_by_ingestion):
        timestamp = available_by_ingestion[ingestion_index][1].ingested_at
        availability_group: list[tuple[int, _Event]] = []
        while (
            ingestion_index < len(available_by_ingestion)
            and available_by_ingestion[ingestion_index][1].ingested_at == timestamp
        ):
            availability_group.append(available_by_ingestion[ingestion_index])
            ingestion_index += 1

        cutoff = timestamp - WINDOW
        for user_id in {event.user_id for _, event in availability_group}:
            available_user_history[user_id].expire(cutoff)
        for item_id in {event.item_id for _, event in availability_group}:
            available_item_history[item_id].expire(cutoff)
        for sequence, event in availability_group:
            if cutoff < event.created_at <= timestamp:
                available_user_history[event.user_id].add(
                    event.created_at, event.event_type, sequence
                )
                available_item_history[event.item_id].add(
                    event.created_at, event.event_type, sequence
                )
        for sequence, event in availability_group:
            if event.ingested_at < event.created_at:
                continue
            user_events = available_user_history[event.user_id]
            item_events = available_item_history[event.item_id]
            available_rows.append(
                {
                    "user_id": event.user_id,
                    "item_id": event.item_id,
                    "event_timestamp": timestamp,
                    "created_timestamp": event.ingested_at,
                    "user_event_count_7d": user_events.event_count,
                    "user_click_count_7d": user_events.click_count,
                    "item_event_count_7d": item_events.event_count,
                    "item_click_count_7d": item_events.click_count,
                }
            )

    snapshot = pd.DataFrame(
        [*rows, *available_rows],
        columns=pd.Index(
            [
                "user_id",
                "item_id",
                "event_timestamp",
                "created_timestamp",
                *FEATURE_COLUMNS,
            ]
        ),
    )
    return snapshot.sort_values(
        ["event_timestamp", "created_timestamp"], kind="stable"
    ).reset_index(drop=True)


def write_feature_snapshot(events: pd.DataFrame, destination: Path) -> Path:
    """Build and write a Feast-compatible Parquet feature source."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    build_feature_snapshot(events).to_parquet(destination, index=False)
    return destination


def write_feature_sources(events: pd.DataFrame, destination_dir: Path) -> tuple[Path, Path]:
    """Write independent user and item sources for their respective Feast keys."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_feature_snapshot(events)
    user_path = destination_dir / "user_interaction_features.parquet"
    item_path = destination_dir / "item_interaction_features.parquet"
    user_source = snapshot[
        ["user_id", "event_timestamp", "created_timestamp", *USER_FEATURE_COLUMNS]
    ].assign(_entity_timestamp="user")
    user_source["_entity_timestamp"] = (
        user_source["user_id"]
        .astype(str)
        .str.cat(user_source["event_timestamp"].astype(str), sep="|")
    )
    user_source.drop_duplicates(subset="_entity_timestamp").drop(
        columns="_entity_timestamp"
    ).to_parquet(user_path, index=False)
    item_source = snapshot[
        ["item_id", "event_timestamp", "created_timestamp", *ITEM_FEATURE_COLUMNS]
    ].assign(_entity_timestamp="item")
    item_source["_entity_timestamp"] = (
        item_source["item_id"]
        .astype(str)
        .str.cat(item_source["event_timestamp"].astype(str), sep="|")
    )
    item_source.drop_duplicates(subset="_entity_timestamp").drop(
        columns="_entity_timestamp"
    ).to_parquet(item_path, index=False)
    return user_path, item_path
