package mlops.streaming.eventslake;

import java.util.Optional;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.configuration.CheckpointingOptions;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.core.execution.CheckpointingMode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.util.Collector;
import org.apache.iceberg.flink.TableLoader;
import org.apache.iceberg.flink.sink.IcebergSink;
import org.apache.iceberg.flink.util.FlinkCompatibilityUtil;

/**
 * Lands raw interaction events into the {@code mlops_lake.events_raw} Iceberg table on MinIO.
 * Commits ride Flink checkpoints (exactly-once); malformed envelopes are filtered, never crash.
 *
 * <p>Dual-pin note (ADR 0008): this job compiles against Flink 2.1.3 + iceberg-flink-runtime-2.1
 * until Iceberg ships a -2.2 runtime; event-counts stays on 2.2.1 meanwhile.
 */
public final class EventsLakeJob {

    public static final String TOPIC = "mlops.events.raw";
    public static final String GROUP_ID = "mlops-flink-events-lake";
    public static final String JOB_NAME = "events-lake";

    private EventsLakeJob() {}

    public static void main(String[] args) throws Exception {
        var bootstrap =
                Optional.ofNullable(System.getenv("KAFKA_BOOTSTRAP_SERVERS")).orElse("localhost:29094");

        var env = StreamExecutionEnvironment.getExecutionEnvironment(envConfig());
        configureCheckpoints(env);

        var source = KafkaSource.<String>builder()
                .setBootstrapServers(bootstrap)
                .setTopics(TOPIC)
                .setGroupId(GROUP_ID)
                .setStartingOffsets(OffsetsInitializer.latest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();

        var wire = env.fromSource(source, WatermarkStrategy.noWatermarks(), "raw-events-kafka-source");
        var rows = toRows(parse(wire));

        // Bootstrap namespace/table through a throwaway catalog; its JDBC pool is released
        // immediately — the sink reopens tables lazily through its own loader.
        var catalogLoader = LakeCatalog.loader(LakeCatalog.propertiesFromEnv());
        org.apache.iceberg.Table table;
        var bootstrapCatalog = catalogLoader.loadCatalog();
        try {
            table = LakeCatalog.ensureTable(bootstrapCatalog);
        } finally {
            if (bootstrapCatalog instanceof AutoCloseable closeable) {
                try {
                    closeable.close();
                } catch (Exception e) {
                    // pool cleanup only; the job runs on its own loaders from here
                }
            }
        }

        IcebergSink.forRowData(rows)
                .tableLoader(TableLoader.fromCatalog(catalogLoader, LakeCatalog.TABLE_ID))
                .table(table)
                .writeParallelism(1)
                .uidSuffix(JOB_NAME)
                .append();

        env.execute(JOB_NAME);
    }

    /** JSON envelopes to valid lake events; malformed input is filtered. */
    public static DataStream<LakeEvent> parse(DataStream<String> wire) {
        return wire.flatMap((String line, Collector<LakeEvent> out) ->
                        EventParser.parse(line).ifPresent(out::collect))
                .returns(LakeEvent.class);
    }

    /** Column order is positional in the sink — {@link LakeRows} mirrors {@link EventsSchema}. */
    public static DataStream<org.apache.flink.table.data.RowData> toRows(DataStream<LakeEvent> events) {
        return events.map(LakeRows::toRow, FlinkCompatibilityUtil.toTypeInfo(EventsSchema.flinkRowType()));
    }

    static void configureCheckpoints(StreamExecutionEnvironment env) {
        env.enableCheckpointing(10_000L);
        var cfg = env.getCheckpointConfig();
        cfg.setCheckpointingConsistencyMode(CheckpointingMode.EXACTLY_ONCE);
        cfg.setMinPauseBetweenCheckpoints(5_000L);
        cfg.setCheckpointTimeout(60_000L);
        cfg.setTolerableCheckpointFailureNumber(3);
    }

    static Configuration envConfig() {
        var config = new Configuration();
        // Same embedded constraint as event-counts: parallelism>1 never fires downstream logic
        // in LocalStreamEnvironment; revisit with the deployment-shape ADR.
        config.set(CoreOptions.DEFAULT_PARALLELISM, Integer.getInteger("flink.parallelism", 1));
        // separate dir from event-counts so both jobs can run concurrently on one box
        config.set(CheckpointingOptions.CHECKPOINT_STORAGE, "filesystem");
        config.set(CheckpointingOptions.CHECKPOINTS_DIRECTORY, "file:///tmp/flink-checkpoints-lake");
        return config;
    }
}
