package mlops.streaming.eventslake;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.time.Instant;
import org.apache.flink.table.data.RowData;
import org.apache.flink.table.data.StringData;
import org.apache.flink.table.data.TimestampData;
import org.junit.jupiter.api.Test;

class LakeRowsTest {

    private static final Instant CREATED = Instant.parse("2026-08-26T09:59:59.123456Z");
    private static final Instant INGESTED = Instant.parse("2026-08-26T10:00:00.000789Z");

    @Test
    void mapsAllFiveFieldsPositionally() {
        RowData row = LakeRows.toRow(new LakeEvent("u1", "i2", "impression", CREATED, INGESTED));

        assertEquals(StringData.fromString("u1"), row.getString(0));
        assertEquals(StringData.fromString("i2"), row.getString(1));
        assertEquals(StringData.fromString("impression"), row.getString(2));
        // micros precision end-to-end: gateway stamps carry sub-millisecond nanos
        assertEquals(CREATED, row.getTimestamp(3, 6).toInstant());
        assertEquals(INGESTED, row.getTimestamp(4, 6).toInstant());
    }
}
