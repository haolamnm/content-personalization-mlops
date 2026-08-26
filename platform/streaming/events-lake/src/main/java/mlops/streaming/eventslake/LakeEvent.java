package mlops.streaming.eventslake;

import java.time.Instant;
import java.util.Set;

/** One interaction event bound for the lakehouse table; ingested_at is stamped at parse time. */
public record LakeEvent(
        String userId, String itemId, String eventType, Instant createdAt, Instant ingestedAt) {

    public static final Set<String> EVENT_TYPES =
            Set.of("impression", "click", "dwell", "like", "share");

    public boolean isValid() {
        return userId != null
                && !userId.isBlank()
                && itemId != null
                && !itemId.isBlank()
                && eventType != null
                && EVENT_TYPES.contains(eventType)
                && createdAt != null
                && ingestedAt != null;
    }
}
