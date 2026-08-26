from datetime import timedelta

from feast import Entity, FeatureService, FeatureView, Field, FileSource, ValueType
from feast.types import Int64

user = Entity(
    name="user",
    value_type=ValueType.STRING,
    join_keys=["user_id"],
    description="A platform user",
)
item = Entity(
    name="item",
    value_type=ValueType.STRING,
    join_keys=["item_id"],
    description="A content item",
)

user_interaction_features_source = FileSource(
    name="user_interaction_features_source",
    path="data/user_interaction_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

item_interaction_features_source = FileSource(
    name="item_interaction_features_source",
    path="data/item_interaction_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

user_interaction_features = FeatureView(
    name="user_interaction_features",
    entities=[user],
    ttl=timedelta(days=7),
    schema=[
        Field(name="user_event_count_7d", dtype=Int64),
        Field(name="user_click_count_7d", dtype=Int64),
    ],
    online=True,
    source=user_interaction_features_source,
    description="Causally safe seven-day user interaction counts at event time",
)

item_interaction_features = FeatureView(
    name="item_interaction_features",
    entities=[item],
    ttl=timedelta(days=7),
    schema=[
        Field(name="item_event_count_7d", dtype=Int64),
        Field(name="item_click_count_7d", dtype=Int64),
    ],
    online=True,
    source=item_interaction_features_source,
    description="Causally safe seven-day item interaction counts at event time",
)

ranking_features = FeatureService(
    name="ranking_features",
    features=[user_interaction_features, item_interaction_features],
    description="The feature vector shared by training and online ranking",
)
