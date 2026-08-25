package mlops.streaming.eventcounts;

import java.time.Instant;
import java.util.Set;

/** One interaction event as consumed from {@code mlops.events.raw}. */
public record RawEvent(String userId, String itemId, String eventType, Instant createdAt) {

    public static final Set<String> EVENT_TYPES =
            Set.of("impression", "click", "dwell", "like", "share");

    public boolean isValid() {
        return userId != null
                && !userId.isBlank()
                && itemId != null
                && !itemId.isBlank()
                && eventType != null
                && EVENT_TYPES.contains(eventType)
                && createdAt != null;
    }
}
