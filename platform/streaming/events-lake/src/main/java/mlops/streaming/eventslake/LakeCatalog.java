package mlops.streaming.eventslake;

import java.util.Map;
import org.apache.iceberg.PartitionSpec;
import org.apache.iceberg.Table;
import org.apache.iceberg.aws.s3.S3FileIO;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.catalog.Namespace;
import org.apache.iceberg.catalog.SupportsNamespaces;
import org.apache.iceberg.catalog.TableIdentifier;
import org.apache.iceberg.exceptions.AlreadyExistsException;
import org.apache.iceberg.exceptions.NoSuchTableException;
import org.apache.iceberg.flink.CatalogLoader;
import org.apache.iceberg.jdbc.JdbcCatalog;

/**
 * Wires the Iceberg JDBC catalog (state in our own Postgres) to the MinIO warehouse
 * ({@code s3://<bucket>}). Namespace and table are ensured idempotently so the job can be the
 * first thing to touch a fresh database or bucket.
 */
public final class LakeCatalog {

    public static final String NAMESPACE = "mlops_lake";
    public static final String TABLE = "events_raw";
    public static final TableIdentifier TABLE_ID = TableIdentifier.of(NAMESPACE, TABLE);

    /** 128 MiB: keeps Parquet files reasonably sized at dev commit cadence without tuning. */
    static final String TARGET_FILE_SIZE = "134217728";

    private LakeCatalog() {}

    public static Map<String, String> properties(
            String jdbcUrl,
            String user,
            String password,
            String warehouse,
            String s3Endpoint,
            String accessKey,
            String secretKey) {
        return Map.ofEntries(
                Map.entry("uri", jdbcUrl),
                Map.entry("warehouse", warehouse),
                Map.entry("jdbc.user", user),
                Map.entry("jdbc.password", password),
                Map.entry("io-impl", S3FileIO.class.getName()),
                Map.entry("s3.endpoint", s3Endpoint),
                // explicit creds: the AWS default chain finds nothing in a bare JRE container
                Map.entry("s3.access-key-id", accessKey),
                Map.entry("s3.secret-access-key", secretKey),
                Map.entry("s3.path-style-access", "true"),
                // S3FileIO requires a region even for MinIO; any value works
                Map.entry("client.region", "us-east-1"));
    }

    /**
     * Environment-driven defaults match host-run development against the compose data group.
     * Credential vars reuse the compose names so one `.env` serves both.
     */
    public static Map<String, String> propertiesFromEnv() {
        var env = System.getenv();
        return properties(
                env.getOrDefault("PG_JDBC_URL", "jdbc:postgresql://localhost:5432/mlops"),
                env.getOrDefault("PG_USER", "mlops"),
                env.getOrDefault("PG_PASSWORD", "mlops"),
                env.getOrDefault("LAKE_WAREHOUSE", "s3://mlops-lake"),
                env.getOrDefault("MINIO_S3_ENDPOINT", "http://localhost:9000"),
                env.getOrDefault("MINIO_ROOT_USER", "minioadmin"),
                env.getOrDefault("MINIO_ROOT_PASSWORD", "minioadmin"));
    }

    public static CatalogLoader loader(Map<String, String> props) {
        return CatalogLoader.custom(
                NAMESPACE, props, new org.apache.hadoop.conf.Configuration(), JdbcCatalog.class.getName());
    }

    /** Creates namespace/table when missing; returns the live table for the sink wiring. */
    public static Table ensureTable(Catalog catalog) {
        if (catalog instanceof SupportsNamespaces nsCatalog) {
            var namespace = Namespace.of(NAMESPACE);
            try {
                nsCatalog.createNamespace(namespace);
            } catch (AlreadyExistsException ignored) {
                // concurrent bootstrap or rerun — fine
            }
        }
        try {
            return catalog.loadTable(TABLE_ID);
        } catch (NoSuchTableException e) {
            try {
                var schema = EventsSchema.schema();
                return catalog.createTable(
                        TABLE_ID,
                        schema,
                        EventsSchema.spec(schema),
                        Map.of("write.target-file-size-bytes", TARGET_FILE_SIZE));
            } catch (AlreadyExistsException race) {
                // concurrent cold start against a fresh database — loser adopts the winner's table
                return catalog.loadTable(TABLE_ID);
            }
        }
    }

    /** Partition-spec accessor for tests that must not rebuild a Schema by hand. */
    public static PartitionSpec spec() {
        return EventsSchema.spec(EventsSchema.schema());
    }
}
