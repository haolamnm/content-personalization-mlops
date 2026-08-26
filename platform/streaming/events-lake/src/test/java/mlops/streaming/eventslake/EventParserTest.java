package mlops.streaming.eventslake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class EventParserTest {

    private static final Instant NOW = Instant.parse("2026-08-26T10:00:00Z");

    @Test
    void parsesValidEnvelopeAndStampsIngestion() {
        var event = EventParser.parse(
                """
                {"user_id":"u1","item_id":"i9","event_type":"click",
                 "created_at":"2026-08-26T09:59:59Z"}""",
                NOW);
        assertTrue(event.isPresent());
        assertEquals("u1", event.get().userId());
        assertEquals("i9", event.get().itemId());
        assertEquals("click", event.get().eventType());
        assertEquals(Instant.parse("2026-08-26T09:59:59Z"), event.get().createdAt());
        assertEquals(NOW, event.get().ingestedAt());
    }

    @Test
    void unknownEventTypeIsRejected() {
        assertTrue(
                EventParser.parse(
                        "{\"user_id\":\"u\",\"item_id\":\"i\",\"event_type\":\"hover\","
                                + "\"created_at\":\"2026-08-26T09:59:59Z\"}",
                        NOW)
                        .isEmpty());
    }

    @Test
    void missingCreatedAtIsRejectedWithoutCrashing() {
        assertTrue(EventParser.parse("{\"user_id\":\"u\",\"item_id\":\"i\",\"event_type\":\"like\"}", NOW).isEmpty());
    }

    @Test
    void nullLiteralMapsToEmpty() {
        assertTrue(EventParser.parse("null", NOW).isEmpty());
    }

    @Test
    void blankAndMalformedAreEmpty() {
        assertTrue(EventParser.parse("", NOW).isEmpty());
        assertTrue(EventParser.parse("not json {", NOW).isEmpty());
    }

    @Test
    void blankUserIdFailsValidation() {
        assertTrue(
                EventParser.parse(
                        "{\"user_id\":\" \",\"item_id\":\"i\",\"event_type\":\"share\","
                                + "\"created_at\":\"2026-08-26T09:59:59Z\"}",
                        NOW)
                        .isEmpty());
    }

    @Test
    void unknownEnvelopeFieldsAreIgnored() {
        var event = EventParser.parse(
                """
                {"user_id":"u1","item_id":"i1","event_type":"dwell",
                 "created_at":"2026-08-26T09:59:59Z","extra":123}""",
                NOW);
        assertTrue(event.isPresent());
    }
}
