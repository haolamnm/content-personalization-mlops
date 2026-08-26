package mlops.streaming.eventslake;

import org.apache.flink.table.data.GenericRowData;
import org.apache.flink.table.data.RowData;
import org.apache.flink.table.data.StringData;
import org.apache.flink.table.data.TimestampData;

/**
 * {@link LakeEvent} to Flink internal row. Field order mirrors {@link EventsSchema#flinkRowType()}
 * exactly — the sink maps columns positionally, not by name.
 */
public final class LakeRows {

    private LakeRows() {}

    public static RowData toRow(LakeEvent event) {
        var row = new GenericRowData(5);
        row.setField(0, StringData.fromString(event.userId()));
        row.setField(1, StringData.fromString(event.itemId()));
        row.setField(2, StringData.fromString(event.eventType()));
        row.setField(3, TimestampData.fromInstant(event.createdAt()));
        row.setField(4, TimestampData.fromInstant(event.ingestedAt()));
        return row;
    }
}
