package mlops.streaming.eventcounts;

import java.time.Duration;
import java.util.Optional;
import org.apache.flink.api.common.eventtime.Watermark;
import org.apache.flink.api.common.eventtime.WatermarkGenerator;
import org.apache.flink.api.common.eventtime.WatermarkOutput;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.configuration.CheckpointingOptions;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.configuration.PipelineOptions;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.core.execution.CheckpointingMode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

/**
 * First Flink job: consumes raw interaction events and counts them per event_type in 10s event-time
 * tumbling windows. Too-late events are side-output, never dropped silently.
 *
 * <p>Runs embedded (LocalStreamEnvironment) via {@code java -jar}; checkpoint storage is a local
 * dev directory — durable state backend comes with the deployment design (see AGENTS.md).
 */
public final class EventCountsJob {

    public static final String TOPIC = "mlops.events.raw";
    public static final String GROUP_ID = "mlops-flink-event-counts";

    /** Window length for per-type counts; also the effective output cadence. */
    static final Duration WINDOW_SIZE = Duration.ofSeconds(10);
    /** How far behind the watermark events may arrive and still be counted. */
    static final Duration ALLOWED_LATENESS = Duration.ofSeconds(5);
    /** Out-of-orderness bound for watermark generation over gateway-stamped created_at. */
    static final Duration WATERMARK_OUT_OF_ORDERNESS = Duration.ofSeconds(2);

    private EventCountsJob() {}

    public static void main(String[] args) throws Exception {
        var bootstrap = Optional.ofNullable(System.getenv("KAFKA_BOOTSTRAP_SERVERS")).orElse("localhost:29094");

        var env = StreamExecutionEnvironment.getExecutionEnvironment(envConfig());
        configureCheckpoints(env);

        var source = KafkaSource.<String>builder()
                .setBootstrapServers(bootstrap)
                .setTopics(TOPIC)
                .setGroupId(GROUP_ID)
                .setStartingOffsets(OffsetsInitializer.latest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                // connector 5.x commits offsets on checkpoints automatically; no knob anymore
                .build();

        var wire = env.fromSource(
                source,
                WatermarkStrategy.noWatermarks(),
                "raw-events-kafka-source");

        var events = parse(wire).assignTimestampsAndWatermarks(watermarks());
        var lateTag = lateTag();
        var counts = countByType(events, lateTag);
        counts.print();
        counts.getSideOutput(lateTag).print("TOO-LATE");

        env.execute("event-counts");
    }

    /** JSON envelopes to valid events; malformed input is filtered (rate metrics come with observability phase). */
    public static DataStream<RawEvent> parse(DataStream<String> wire) {
        return wire.flatMap((String line, Collector<RawEvent> out) -> EventParser.parse(line).ifPresent(out::collect))
                .returns(RawEvent.class);
    }

    /**
     * Core production strategy: punctuated per-record watermarks with bounded-out-of-orderness
     * semantics — each event advances the running max and emits max-2s. Chosen over the periodic
     * emitter after it proved unreliable in embedded runs; identical behavior in real clusters.
     * Kept free of deployment wrappers so unit tests exercise exactly this logic.
     */
    public static WatermarkStrategy<RawEvent> boundedPunctuatedWatermarks() {
        return WatermarkStrategy.<RawEvent>forGenerator(ctx -> new WatermarkGenerator<>() {
                    private long maxTimestamp = Long.MIN_VALUE;

                    @Override
                    public void onEvent(RawEvent event, long ts, WatermarkOutput out) {
                        maxTimestamp = Math.max(maxTimestamp, ts);
                        out.emitWatermark(new Watermark(maxTimestamp - WATERMARK_OUT_OF_ORDERNESS.toMillis()));
                    }

                    @Override
                    public void onPeriodicEmit(WatermarkOutput out) {}
                })
                .withTimestampAssigner((event, ts) -> event.createdAt().toEpochMilli());
    }

    /**
     * Production assembly: core strategy + idleness so partitions with no traffic cannot pin the
     * merged watermark at -inf. The idleness wrapper itself misbehaves in fast finite batches
     * (unit scope), hence the split — remote e2e validates the assembled form.
     */
    public static WatermarkStrategy<RawEvent> watermarks() {
        return boundedPunctuatedWatermarks().withIdleness(Duration.ofSeconds(2));
    }

    public static OutputTag<RawEvent> lateTag() {
        return new OutputTag<>("too-late", TypeInformation.of(RawEvent.class));
    }

    public static SingleOutputStreamOperator<String> countByType(DataStream<RawEvent> events, OutputTag<RawEvent> lateTag) {
        return events
                .keyBy(RawEvent::eventType)
                .window(TumblingEventTimeWindows.of(WINDOW_SIZE))
                .allowedLateness(ALLOWED_LATENESS)
                .sideOutputLateData(lateTag)
                .aggregate(new Count(), new Format());
    }

    static void configureCheckpoints(StreamExecutionEnvironment env) {
        // interval + tolerance are the documented resilience knobs — see AGENTS.md
        env.enableCheckpointing(10_000L);
        var cfg = env.getCheckpointConfig();
        cfg.setCheckpointingConsistencyMode(CheckpointingMode.EXACTLY_ONCE);
        cfg.setMinPauseBetweenCheckpoints(5_000L);
        cfg.setCheckpointTimeout(60_000L);
        cfg.setTolerableCheckpointFailureNumber(3);
    }

    /** Environment configuration: dev checkpoint storage is a local directory (see AGENTS.md). */
    static Configuration envConfig() {
        var config = new Configuration();
        // Embedded LocalStreamEnvironment at parallelism>1 never fires event-time windows:
        // watermarks are emitted upstream but the window operator's valve never releases
        // (reproduced in-process, see AGENTS.md "Known constraint"). Real clusters are unaffected;
        // revisit parallelism with the deployment-shape ADR. Override locally: -Dflink.parallelism=N
        config.set(CoreOptions.DEFAULT_PARALLELISM, Integer.getInteger("flink.parallelism", 1));
        config.set(PipelineOptions.AUTO_WATERMARK_INTERVAL, Duration.ofMillis(200));
        config.set(CheckpointingOptions.CHECKPOINT_STORAGE, "filesystem");
        // env override enables durable/restore-capable deployments (matches events-lake)
        config.set(
                CheckpointingOptions.CHECKPOINTS_DIRECTORY,
                Optional.ofNullable(System.getenv("CHECKPOINTS_DIRECTORY"))
                        .orElse("file:///tmp/flink-checkpoints"));
        return config;
    }

    static final class Count implements AggregateFunction<RawEvent, Long, Long> {
        @Override
        public Long createAccumulator() {
            return 0L;
        }

        @Override
        public Long add(RawEvent value, Long acc) {
            return acc + 1;
        }

        @Override
        public Long getResult(Long acc) {
            return acc;
        }

        @Override
        public Long merge(Long a, Long b) {
            return a + b;
        }
    }

    static final class Format extends ProcessWindowFunction<Long, String, String, TimeWindow> {
        @Override
        public void process(String type, Context ctx, Iterable<Long> counts, Collector<String> out) {
            var window = ctx.window();
            out.collect("%s count=%d window=[%ds..%ds)".formatted(type, counts.iterator().next(), window.getStart() / 1000, window.getEnd() / 1000));
        }
    }
}
