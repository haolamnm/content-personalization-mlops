package mlops.streaming.eventcounts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.stream.Collectors;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.connector.sink2.Sink;
import org.apache.flink.api.connector.sink2.SinkWriter;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.util.OutputTag;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

/** Deterministic MiniCluster tests: in-memory source with ascending event time, results collected via Sink V2. */
class EventCountsPipelineTest {

    private static final List<String> COLLECTED = new CopyOnWriteArrayList<>();
    private static final List<RawEvent> LATE = new CopyOnWriteArrayList<>();

    @AfterEach
    void reset() {
        COLLECTED.clear();
        LATE.clear();
    }

    private static Instant at(int second) {
        return Instant.ofEpochSecond(1_800_000_000L + second);
    }

    private static String envelope(String user, String type, int second) {
        return "{\"user_id\":\"%s\",\"item_id\":\"i1\",\"event_type\":\"%s\",\"created_at\":\"%s\"}"
                .formatted(user, type, at(second));
    }

    /** Runs the real pipeline over an ordered finite stream; MAX_WATERMARK closes every window. */
    private void run(List<String> envelopes) throws Exception {
        var config = new Configuration();
        config.set(CoreOptions.DEFAULT_PARALLELISM, 1);
        var env = StreamExecutionEnvironment.getExecutionEnvironment(config);

        DataStream<String> wire = env.fromCollection(envelopes).name("in-memory-wire");
        // punctuated per-record watermarks: deterministic in a fast finite batch where
        // periodic emission would never fire between records
        var events = EventCountsJob.parse(wire)
                .assignTimestampsAndWatermarks(punctuatedFromRecords());

        var lateTag = EventCountsJob.lateTag();
        var counts = EventCountsJob.countByType(events, lateTag);
        counts.sinkTo(new CollectingSink());
        counts.getSideOutput(lateTag).sinkTo(new LateSink());

        env.execute();
        awaitResults(envelopes.size());
    }

    private static org.apache.flink.api.common.eventtime.WatermarkStrategy<RawEvent> punctuatedFromRecords() {
        return org.apache.flink.api.common.eventtime.WatermarkStrategy.<RawEvent>forGenerator(ctx -> new org.apache.flink.api.common.eventtime.WatermarkGenerator<>() {
            private long maxTs = Long.MIN_VALUE;

            @Override
            public void onEvent(RawEvent event, long ts, org.apache.flink.api.common.eventtime.WatermarkOutput out) {
                maxTs = Math.max(maxTs, ts);
                out.emitWatermark(new org.apache.flink.api.common.eventtime.Watermark(maxTs));
            }

            @Override
            public void onPeriodicEmit(org.apache.flink.api.common.eventtime.WatermarkOutput out) {}
        }).withTimestampAssigner((e, ts) -> e.createdAt().toEpochMilli());
    }

    private static void awaitResults(int inputSize) throws InterruptedException {
        long deadline = System.nanoTime() + Duration.ofSeconds(30).toNanos();
        while (System.nanoTime() < deadline) {
            if (!COLLECTED.isEmpty() || !LATE.isEmpty()) {
                return; // windows closed; exact assertions follow
            }
            Thread.sleep(50);
        }
        assertTrue(false, "no results within timeout for input size " + inputSize);
    }

    @Test
    void countsEventsPerTypeInTumblingWindows() throws Exception {
        // 3 clicks + 2 impressions inside the same 10s window, then a click in the next window
        run(List.of(
                envelope("u1", "click", 0),
                envelope("u2", "click", 3),
                envelope("u1", "impression", 4),
                envelope("u3", "click", 9),
                envelope("u4", "impression", 5),
                envelope("u5", "click", 12)));

        // click spans two windows: 3 events in [..10s) + 1 in [10s..20s); impression has 2
        assertEquals(3, COLLECTED.size(), "one result line per (type, window): " + COLLECTED);
        var window1 = COLLECTED.stream().filter(l -> l.contains("[1800000000s")).toList();
        var byType = window1.stream().collect(Collectors.toMap(l -> l.split(" ")[0], l -> l));
        assertTrue(byType.get("click").contains("count=3"), byType.get("click"));
        assertTrue(byType.get("impression").contains("count=2"), byType.get("impression"));
        assertTrue(COLLECTED.stream().anyMatch(l -> l.startsWith("click ") && l.contains("count=1") && l.contains("[1800000010s")), "late-window click counted: " + COLLECTED);
        assertTrue(LATE.isEmpty());
    }

    @Test
    void tooLateEventsGoToSideOutputNotSilentlyDropped() throws Exception {
        // production bound is 2s; this generator emits raw maxTs (stricter), so an event 60s
        // behind its predecessor is equally guaranteed to land in the side output
        run(List.of(
                envelope("u1", "click", 100),
                envelope("u2", "click", 40)));

        assertTrue(COLLECTED.size() >= 1, "on-time window still emits: " + COLLECTED);
        assertEquals(1, LATE.size(), "the far-behind event must land in the side output");
        assertEquals("u2", LATE.getFirst().userId());
    }

    @Test
    void malformedLinesAreFilteredBeforeWindowing() throws Exception {
        run(List.of(
                "{not json",
                envelope("u1", "share", 1),
                envelope("u2", "hover", 2)));

        assertEquals(1, COLLECTED.size(), "only the valid share survives: " + COLLECTED);
        assertTrue(COLLECTED.getFirst().startsWith("share "), COLLECTED.getFirst());
        assertTrue(LATE.isEmpty());
    }

    // --- Sink V2 collectors (SinkFunction was removed in Flink 2.x) ---

    public static final class CollectingSink implements Sink<String> {
        @Override
        public SinkWriter<String> createWriter(org.apache.flink.api.connector.sink2.WriterInitContext ctx) {
            return new SinkWriter<>() {
                @Override
                public void write(String element, Context context) {
                    COLLECTED.add(element);
                }

                @Override
                public void flush(boolean endOfInput) {}

                @Override
                public void close() {}
            };
        }
    }

    public static final class LateSink implements Sink<RawEvent> {
        @Override
        public SinkWriter<RawEvent> createWriter(org.apache.flink.api.connector.sink2.WriterInitContext ctx) {
            return new SinkWriter<>() {
                @Override
                public void write(RawEvent element, Context context) {
                    LATE.add(element);
                }

                @Override
                public void flush(boolean endOfInput) {}

                @Override
                public void close() {}
            };
        }
    }
}
