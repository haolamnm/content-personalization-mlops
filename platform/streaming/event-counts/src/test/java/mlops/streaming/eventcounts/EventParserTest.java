package mlops.streaming.eventcounts;

import static org.junit.jupiter.api.Assertions.*;

import java.time.Instant;
import org.junit.jupiter.api.Test;

class EventParserTest {

    @Test
    void parsesGatewayEnvelope() {
        var json = """
                {"user_id":"u1","item_id":"i7","event_type":"click","created_at":"2026-08-25T10:15:30Z"}
                """;
        var event = EventParser.parse(json).orElseThrow();
        assertEquals("u1", event.userId());
        assertEquals("i7", event.itemId());
        assertEquals("click", event.eventType());
        assertEquals(Instant.parse("2026-08-25T10:15:30Z"), event.createdAt());
    }

    @Test
    void rejectsUnknownEventType() {
        var json = """
                {"user_id":"u1","item_id":"i7","event_type":"hover","created_at":"2026-08-25T10:15:30Z"}
                """;
        assertTrue(EventParser.parse(json).isEmpty());
    }

    @Test
    void rejectsMalformedJson() {
        assertTrue(EventParser.parse("{not json").isEmpty());
    }

    @Test
    void rejectsBlankAndNull() {
        assertTrue(EventParser.parse("").isEmpty());
        assertTrue(EventParser.parse("   ").isEmpty());
        assertTrue(EventParser.parse(null).isEmpty());
    }

    @Test
    void rejectsMissingFields() {
        assertTrue(EventParser.parse("""
                {"user_id":"u1","event_type":"click","created_at":"2026-08-25T10:15:30Z"}
                """).isEmpty());
        assertTrue(EventParser.parse("""
                {"item_id":"i7","event_type":"click","created_at":"2026-08-25T10:15:30Z"}
                """).isEmpty());
    }

    @Test
    void rejectsMissingOrNullCreatedAtWithoutThrowing() {
        // absent created_at must yield empty, not NPE — a thrown exception here would
        // fail the whole job and loop on the same poison record after checkpoint restart
        assertTrue(EventParser.parse("""
                {"user_id":"u1","item_id":"i7","event_type":"click"}
                """).isEmpty());
        assertTrue(EventParser.parse("""
                {"user_id":"u1","item_id":"i7","event_type":"click","created_at":null}
                """).isEmpty());
    }

    @Test
    void rejectsBadTimestamp() {
        assertTrue(EventParser.parse("""
                {"user_id":"u1","item_id":"i7","event_type":"click","created_at":"yesterday"}
                """).isEmpty());
    }
}
