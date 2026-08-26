package mlops.streaming.eventslake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import org.apache.iceberg.PartitionField;
import org.apache.iceberg.Schema;
import org.apache.iceberg.types.Types;
import org.junit.jupiter.api.Test;

class EventsSchemaTest {

    @Test
    void schemaHasFiveColumnsInContractOrder() {
        Schema schema = EventsSchema.schema();
        assertEquals(
                java.util.List.of("user_id", "item_id", "event_type", "created_at", "ingested_at"),
                schema.columns().stream().map(Types.NestedField::name).toList());
    }

    @Test
    void timestampsAreTimestamptz() {
        var schema = EventsSchema.schema();
        assertEquals(Types.TimestampType.withZone(), schema.findField("created_at").type());
        assertEquals(Types.TimestampType.withZone(), schema.findField("ingested_at").type());
    }

    @Test
    void tableIsPartitionedByDayOfCreatedAt() {
        var spec = LakeCatalog.spec();
        assertEquals(1, spec.fields().size());
        PartitionField field = spec.fields().get(0);
        assertEquals("created_at", spec.schema().findColumnName(field.sourceId()));
        assertEquals("day", field.transform().toString());
        assertFalse(spec.isUnpartitioned());
    }

    @Test
    void flinkRowTypeMatchesSchemaColumnOrder() {
        // the sink maps positionally: this guard fails loudly if the two ever diverge
        var rowType = EventsSchema.flinkRowType();
        assertEquals(5, rowType.getFieldCount());
        for (int i = 0; i < 5; i++) {
            assertEquals(
                    EventsSchema.schema().columns().get(i).name(),
                    rowType.getFields().get(i).getName());
        }
    }
}
