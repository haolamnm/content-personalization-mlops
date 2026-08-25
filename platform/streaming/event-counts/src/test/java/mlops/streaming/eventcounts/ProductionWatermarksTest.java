package mlops.streaming.eventcounts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

/**
 * Exercises the production {@link EventCountsJob#watermarks()} — punctuated emission with the real
 * −2s out-of-orderness bound — which the pipeline tests' stricter maxTs generator does not cover.
 */
class ProductionWatermarksTest {

    private static final List<String> COLLECTED = new java.util.concurrent.CopyOnWriteArrayList<>();
    private static final List<RawEvent> LATE = new java.util.concurrent.CopyOnWriteArrayList<>();

    @AfterEach
    void reset() {
        COLLECTED.clear();
        LATE.clear();
    }

    private static String envelope(String user, String type, int second) {
        return "{\"user_id\":\"%s\",\"item_id\":\"i\",\"event_type\":\"%s\",\"created_at\":\"%s\"}"
                .formatted(user, type, Instant.ofEpochSecond(1_800_200_000L + second));
    }

    @Test
    void boundedOutOfOrdernessBoundIsAppliedByProductionStrategy() throws Exception {
        var config = new Configuration();
        config.set(CoreOptions.DEFAULT_PARALLELISM, 1);
        var env = StreamExecutionEnvironment.getExecutionEnvironment(config);

        DataStream<String> wire = env.fromCollection(List.of(
                envelope("u1", "click", 0),
                // 3s behind: beyond the 2s bound → too late for its bucket
                envelope("u2", "click", -3),
                // within bound: counted in the first bucket despite arriving second
                envelope("u3", "click", 8),
                envelope("u9", "share", 20),
                // arrives last with wm already at ~18s: window [-40..-30) cleanup (=-25.001s)
                // is far behind → production strategy itself must side-output it
                envelope("u4", "click", -30)));

        var events = EventCountsJob.parse(wire).assignTimestampsAndWatermarks(EventCountsJob.boundedPunctuatedWatermarks());
        var lateTag = EventCountsJob.lateTag();
        var counts = EventCountsJob.countByType(events, lateTag);
        counts.sinkTo(new LocalCollectingSink());
        counts.getSideOutput(lateTag).sinkTo(new LocalLateSink());

        env.execute();

        long deadline = System.nanoTime() + Duration.ofSeconds(20).toNanos();
        while (System.nanoTime() < deadline && COLLECTED.isEmpty()) {
            Thread.sleep(50);
        }
        // u2 (3s behind) is NOT dropped: it belongs to its own earlier bucket and is still
        // within allowed lateness — the bound shapes watermark progress, not acceptance
        assertEquals(1, LATE.size(), "beyond-bound+lateness event must be side-output by the production strategy: " + LATE);
        assertEquals("u4", LATE.getFirst().userId());
        var clicks = COLLECTED.stream().filter(l -> l.startsWith("click")).toList();
        assertEquals(2, clicks.size(), COLLECTED.toString());
        assertTrue(clicks.stream().anyMatch(l -> l.contains("count=1") && l.contains("[1800199990s")), "early bucket holds only u2: " + clicks);
        assertTrue(clicks.stream().anyMatch(l -> l.contains("count=2") && l.contains("[1800200000s")), "on-time bucket holds u1+u3: " + clicks);
    }

    // local sinks so results land on THIS test's lists, not the shared pipeline-test ones
    private static final class LocalCollectingSink implements org.apache.flink.api.connector.sink2.Sink<String> {
        @Override
        public org.apache.flink.api.connector.sink2.SinkWriter<String> createWriter(org.apache.flink.api.connector.sink2.WriterInitContext ctx) {
            return new org.apache.flink.api.connector.sink2.SinkWriter<>() {
                @Override public void write(String element, org.apache.flink.api.connector.sink2.SinkWriter.Context context) { COLLECTED.add(element); }
                @Override public void flush(boolean endOfInput) {}
                @Override public void close() {}
            };
        }
    }

    private static final class LocalLateSink implements org.apache.flink.api.connector.sink2.Sink<RawEvent> {
        @Override
        public org.apache.flink.api.connector.sink2.SinkWriter<RawEvent> createWriter(org.apache.flink.api.connector.sink2.WriterInitContext ctx) {
            return new org.apache.flink.api.connector.sink2.SinkWriter<>() {
                @Override public void write(RawEvent element, org.apache.flink.api.connector.sink2.SinkWriter.Context context) { LATE.add(element); }
                @Override public void flush(boolean endOfInput) {}
                @Override public void close() {}
            };
        }
    }
}
