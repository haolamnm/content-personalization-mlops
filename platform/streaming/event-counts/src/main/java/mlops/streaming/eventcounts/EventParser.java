package mlops.streaming.eventcounts;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.core.JacksonException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.Optional;

/** Parses raw JSON envelopes from the gateway into {@link RawEvent}s; malformed input yields empty. */
public final class EventParser {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private EventParser() {}

    /** Wire shape mirrors the gateway envelope exactly; explicit over magic. */
    @JsonIgnoreProperties(ignoreUnknown = true)
    private record Wire(String user_id, String item_id, String event_type, String created_at) {}

    public static Optional<RawEvent> parse(String json) {
        if (json == null || json.isBlank()) {
            return Optional.empty();
        }
        try {
            var env = MAPPER.readValue(json, Wire.class);
            if (env == null) {
                return Optional.empty(); // JSON literal "null" maps to a null reference
            }
            // created_at may be absent/null: pass it through and let isValid() reject —
            // Instant.parse would NPE on null, escaping the catch set and crashing the job
            var event = new RawEvent(
                    env.user_id(), env.item_id(), env.event_type(),
                    env.created_at() == null ? null : Instant.parse(env.created_at()));
            return event.isValid() ? Optional.of(event) : Optional.empty();
        } catch (IllegalArgumentException | DateTimeParseException | JacksonException e) {
            return Optional.empty();
        }
    }
}
