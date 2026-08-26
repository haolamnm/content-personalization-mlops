package mlops.streaming.eventslake;

import org.apache.iceberg.PartitionSpec;
import org.apache.iceberg.Schema;
import org.apache.iceberg.flink.FlinkSchemaUtil;
import org.apache.iceberg.types.Types;

/**
 * The lakehouse contract: {@code mlops_lake.events_raw} is append-only, partitioned by day of
 * {@code created_at}. Field ids are part of the schema's identity — never renumber existing
 * columns, only append.
 */
public final class EventsSchema {

    public static final String USER_ID = "user_id";
    public static final String ITEM_ID = "item_id";
    public static final String EVENT_TYPE = "event_type";
    public static final String CREATED_AT = "created_at";
    public static final String INGESTED_AT = "ingested_at";

    private EventsSchema() {}

    public static Schema schema() {
        return new Schema(
                Types.NestedField.required(1, USER_ID, Types.StringType.get()),
                Types.NestedField.required(2, ITEM_ID, Types.StringType.get()),
                Types.NestedField.required(3, EVENT_TYPE, Types.StringType.get()),
                Types.NestedField.required(4, CREATED_AT, Types.TimestampType.withZone()),
                Types.NestedField.optional(5, INGESTED_AT, Types.TimestampType.withZone()));
    }

    public static PartitionSpec spec(Schema schema) {
        return PartitionSpec.builderFor(schema).day(CREATED_AT).build();
    }

    /** Flink internal row type; field order here IS the sink's column order contract. */
    public static org.apache.flink.table.types.logical.RowType flinkRowType() {
        return (org.apache.flink.table.types.logical.RowType) FlinkSchemaUtil.convert(schema());
    }
}
