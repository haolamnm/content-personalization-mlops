# k3s data plane

These manifests and values are the standing THINKBOOK runtime after the Phase 1 cutover. Compose files remain the low-memory authoring venue on MACBOOK, but the box must not run both data planes at once.

The operator pins are Strimzi 1.1.0 with Kafka 4.3.0, CloudNativePG chart 0.29.0 with PostgreSQL 18.6, Bitnami MongoDB chart 16.5.45 with the Bitnami Legacy MongoDB 8.0.13 image, MinIO chart 5.4.0 with the project MinIO image pin, and Bitnami Redis chart 28.0.10 with the Bitnami Legacy Redis 8.0.3 image. MongoDB runs as a single-node replica set because Debezium change streams require a replica set; the Compose fallback remains standalone. MongoDB is restored logically, so the chart image does not copy the Compose data directory across versions.

## Apply order

Run Helm and kubectl from the authoring Mac with the THINKBOOK kubeconfig. Secrets are created on the box from its ignored `.env`; they never belong in these files.

For a repeatable existing-installation cutover, run `make k8s-data-up`; it includes `k8s-mongodb-migrate` before the MongoDB Helm upgrade. The expanded commands below describe the order for a fresh or already-migrated installation.

```bash
export KUBECONFIG="$HOME/.kube/config"
kubectl create namespace mlops-data --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace mlops-streaming --dry-run=client -o yaml | kubectl apply -f -
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm repo add minio https://charts.min.io/
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm upgrade --install strimzi oci://quay.io/strimzi-helm/strimzi-kafka-operator --version 1.1.0 --namespace strimzi-system --create-namespace --set 'watchNamespaces[0]=mlops-data' --wait
helm upgrade --install cnpg cnpg/cloudnative-pg --version 0.29.0 --namespace cnpg-system --create-namespace --wait
kubectl apply -f platform/infra/k8s/kafka.yaml -f platform/infra/k8s/postgres.yaml
helm upgrade --install mlops-mongodb bitnami/mongodb --version 16.5.45 --namespace mlops-data -f platform/infra/k8s/mongodb-values.yaml --wait
helm upgrade --install mlops-minio minio/minio --version 5.4.0 --namespace mlops-data -f platform/infra/k8s/minio-values.yaml --wait
helm upgrade --install mlops-redis bitnami/redis --version 28.0.10 --namespace mlops-data -f platform/infra/k8s/redis-values.yaml --wait
kubectl apply -f platform/infra/k8s/connect.yaml -f platform/infra/k8s/connector-postgres.yaml -f platform/infra/k8s/connector-mongodb.yaml
helm template event-counts platform/streaming/event-counts/chart --namespace mlops-streaming -f platform/infra/k8s/event-counts-values.yaml | kubectl apply -f -
helm template events-lake platform/streaming/events-lake/chart --namespace mlops-streaming -f platform/infra/k8s/events-lake-values.yaml | kubectl apply -f -
helm template gateway platform/services/event-gateway/chart --namespace mlops-gateway -f platform/infra/k8s/gateway-values.yaml | kubectl apply -f -
```

`make k8s-data-up` runs `k8s-mongodb-migrate` before the MongoDB Helm upgrade. If it finds the previous standalone StatefulSet service name, it deletes only the StatefulSet with `--cascade=orphan` and its pod, preserving the PVC, then Helm recreates the replica-set shape. The target is idempotent once `serviceName` is `mlops-mongodb-headless` and refuses an unknown shape.

Create `mlops-postgres-app`, `mongodb-auth`, `minio-credentials`, `redis-auth`, and `events-lake-config` before applying the dependent resources. The Postgres Secret uses `username` and `password`; Mongo uses `mongodb-root-password` and `mongodb-replica-set-key`; MinIO uses `rootUser` and `rootPassword`; Redis uses `redis-password`; the lake secret uses `PG_PASSWORD`, `MINIO_ROOT_USER`, and `MINIO_ROOT_PASSWORD`.

The first migration is a data operation, not a Helm upgrade: take logical PostgreSQL, Mongo archive, Kafka metadata, and MinIO object backups; restore PostgreSQL and MinIO; recreate Kafka topics through `kafka.yaml`; restore Mongo users/data logically; then stop Compose CDC and data containers only after all k8s readiness and content checks pass.

Debezium uses `platform/infra/cdc/Dockerfile.k8s`: it keeps the Strimzi Connect runtime entrypoint and copies the PostgreSQL and MongoDB plugins from `quay.io/debezium/connect:3.6.1.Final`. Build it on THINKBOOK, import it with `mlops-sudo image-import`, and keep `imagePullPolicy: IfNotPresent` for the node-local image.

The PostgreSQL and MongoDB connector passwords are resolved at runtime by Strimzi's Kubernetes Secret ConfigProvider. The `mlops-connect-connect` service account is granted `get` only on `mlops-postgres-app` and `mongodb-auth`; do not replace this with a plaintext connector manifest. MongoDB catalog changes are emitted to `mlops_mongodb.mlops_catalog.content_items`.

## Final cutover gate

```bash
kubectl get kafka/mlops-kafka kafkaconnect/mlops-connect kafkaconnector/postgres-source kafkaconnector/mongodb-source -n mlops-data
kubectl get cluster mlops-postgres -n mlops-data
kubectl get pods -A
docker ps -a --format '{{.Names}}' | rg '^(cdc-connect|data-)'
```

The final command must print no Compose data or CDC containers. The gateway, both Flink jobs, and Debezium must all use `mlops-kafka-kafka-bootstrap.mlops-data.svc.cluster.local:9092`; events-lake must use `mlops-postgres-rw.mlops-data.svc.cluster.local` and `mlops-minio.mlops-data.svc.cluster.local`. Prove the path with a valid `POST /events`, a matching record on `mlops.events.raw`, a fresh Flink checkpoint, and an Iceberg commit.
