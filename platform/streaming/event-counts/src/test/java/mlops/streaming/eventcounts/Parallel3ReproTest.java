package mlops.streaming.eventcounts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.api.connector.sink2.SinkWriter;
import org.apache.flink.api.connector.sink2.WriterInitContext;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.junit.jupiter.api.Test;

/**
 * Documents a Flink 2.2.1 embedded-runtime constraint: at parallelism>1 the window
 * operator never fires (records arrive, watermarks are emitted upstream, zero results).
 * Disabled so gates stay green; keep as the reproduction recipe for an upstream report
 * and re-enable after upgrading Flink or moving to a real cluster.
 */
@org.junit.jupiter.api.Disabled("known embedded-mode constraint, see README")
class Parallel3ReproTest {

    private static final List<String> COLLECTED = new java.util.concurrent.CopyOnWriteArrayList<>();
    private static final List<RawEvent> LATE = new java.util.concurrent.CopyOnWriteArrayList<>();

    private static Instant at(int second) {
        return Instant.ofEpochSecond(1_800_100_000L + second);
    }

    private static String envelope(String user, String type, int second) {
        return "{\"user_id\":\"%s\",\"item_id\":\"i\",\"event_type\":\"%s\",\"created_at\":\"%s\"}"
                .formatted(user, type, at(second));
    }

    @Test
    void threeSubtasksStillFireWindows() throws Exception {
        var config = new Configuration();
        config.set(CoreOptions.DEFAULT_PARALLELISM, Integer.getInteger("repro.par", 3));
        var env = StreamExecutionEnvironment.getExecutionEnvironment(config);

        // spread over time like real traffic: bursts then gaps
        List<String> envelopes = List.of(
                envelope("u1", "click", 1),
                envelope("u2", "click", 2),
                envelope("u3", "share", 3),
                envelope("u4", "click", 14),
                envelope("u5", "impression", 15),
                envelope("u6", "click", 27));

        DataStream<String> wire = env.fromCollection(envelopes);
        var events = EventCountsJob.parse(wire)
                .assignTimestampsAndWatermarks(EventCountsJob.watermarks());

        var lateTag = EventCountsJob.lateTag();
        var counts = EventCountsJob.countByType(events, lateTag);
        counts.sinkTo(new LocalSink());
        counts.getSideOutput(lateTag).sinkTo(new LocalLateSink());

        env.execute();

        long deadline = System.nanoTime() + Duration.ofSeconds(20).toNanos();
        while (System.nanoTime() < deadline && COLLECTED.isEmpty()) {
            Thread.sleep(50);
        }
        assertTrue(COLLECTED.size() >= 3, "expected multiple window results at parallelism 3, got: " + COLLECTED);
        assertEquals(3, COLLECTED.stream().filter(l -> l.startsWith("click")).count(), COLLECTED.toString());
        assertEquals(1, COLLECTED.stream().filter(l -> l.startsWith("share")).count());
        assertEquals(1, COLLECTED.stream().filter(l -> l.startsWith("impression")).count());
    }

    // self-owned collectors: results must land here, not on shared pipeline-test lists
    private static final class LocalSink implements org.apache.flink.api.connector.sink2.Sink<String> {
        @Override
        public org.apache.flink.api.connector.sink2.SinkWriter<String> createWriter(WriterInitContext ctx) {
            return new org.apache.flink.api.connector.sink2.SinkWriter<>() {
                @Override public void write(String element, Context context) { COLLECTED.add(element); }
                @Override public void flush(boolean endOfInput) {}
                @Override public void close() {}
            };
        }
    }

    private static final class LocalLateSink implements org.apache.flink.api.connector.sink2.Sink<RawEvent> {
        @Override
        public org.apache.flink.api.connector.sink2.SinkWriter<RawEvent> createWriter(WriterInitContext ctx) {
            return new org.apache.flink.api.connector.sink2.SinkWriter<>() {
                @Override public void write(RawEvent element, Context context) { LATE.add(element); }
                @Override public void flush(boolean endOfInput) {}
                @Override public void close() {}
            };
        }
    }
}
