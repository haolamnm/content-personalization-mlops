COMPOSE_FILE := platform/infra/compose.data.yaml
COMPOSE := docker compose --env-file .env -f $(COMPOSE_FILE)

.PHONY: data-preflight data-guard data-up data-health data-stats data-down

data-preflight: data-guard
	docker ps
	memory_pressure | head -20
	docker stats --no-stream

data-guard:
	@foreign=$$(docker compose ls --format '{{.Name}}' 2>/dev/null | awk '$$0 != "" && $$0 != "data" && $$0 != "cdc" && $$0 != "gateway"'); \
	if [ -n "$$foreign" ]; then echo "refusing: active compose project(s) outside the sanctioned set:" $$foreign >&2; exit 1; fi

data-up: data-guard
	$(COMPOSE) config -q
	$(COMPOSE) up -d

data-health:
	docker exec data-postgres pg_isready -U $${POSTGRES_USER:-mlops}
	docker exec data-mongodb mongosh --quiet --eval "db.adminCommand('ping').ok"
	docker exec data-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list >/dev/null && echo "kafka: topics listable"
	docker exec data-minio mc ready local && echo "minio: ready"
	docker exec data-redis sh -c 'redis-cli --no-auth-warning -a "$${REDIS_PASSWORD}" ping' | rg -q '^PONG$$' && echo "redis: ready"

data-stats:
	docker stats --no-stream

data-down: cdc-down
	$(COMPOSE) down

COMPOSE_CDC := docker compose --env-file .env -f platform/infra/compose.cdc.yaml

.PHONY: cdc-guard cdc-up cdc-register cdc-schema cdc-health cdc-down

cdc-guard: data-guard
	@status=$$($(COMPOSE_CDC) ps -q connect 2>/dev/null | xargs -r docker inspect -f '{{.State.Health.Status}}' 2>/dev/null); \
	[ "$$status" = "healthy" ] || { echo "cdc-connect not healthy (status: $${status:-absent})" >&2; exit 1; }

cdc-health:
	@bash -c '. "$(CURDIR)/.env" 2>/dev/null; out=$$(curl -fSs "http://localhost:$${CONNECT_HOST_PORT:-8083}/connectors") || exit 1; printf "%.300s\n" "$$out"'

cdc-up: data-guard
	$(COMPOSE) up -d postgres kafka
	$(COMPOSE_CDC) up -d
	@ok=""; for i in $$(seq 1 24); do if $(MAKE) -s cdc-guard 2>/dev/null; then ok=1; break; fi; sleep 5; done; \
	[ -n "$$ok" ] || { echo "cdc-connect failed to become healthy" >&2; exit 1; }

cdc-register: cdc-guard cdc-schema
	bash platform/infra/cdc/register-postgres.sh

cdc-schema:
	docker exec -i data-postgres sh -c 'psql -U "$${POSTGRES_USER}" -d "$${POSTGRES_DB}"' < platform/infra/cdc/schema.sql

cdc-down:
	$(COMPOSE_CDC) down

COMPOSE_GATEWAY := docker compose --env-file .env -f platform/infra/compose.gateway.yaml

.PHONY: gateway-up gateway-health gateway-down topics-ensure

gateway-up: data-guard topics-ensure
	$(COMPOSE_GATEWAY) up -d --build
	@bash -c '. "$(CURDIR)/.env" 2>/dev/null; for i in $$(seq 1 20); do curl -sf "http://localhost:$${GATEWAY_HOST_PORT:-8080}/healthz" >/dev/null 2>&1 && echo GATEWAY-HEALTHY && exit 0; sleep 3; done; echo "gateway failed to become healthy" >&2; exit 1'

topics-ensure:
	docker exec data-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic mlops.events.raw --partitions 3 --replication-factor 1

gateway-health:
	@bash -c '. "$(CURDIR)/.env" 2>/dev/null; curl -fSs "http://localhost:$${GATEWAY_HOST_PORT:-8080}/healthz" && echo'

gateway-down:
	$(COMPOSE_GATEWAY) down

K8S_DIR := platform/infra/k8s
KUBECTL ?= kubectl
HELM ?= helm

.PHONY: features-test features-lint k8s-validate k8s-operators k8s-data-up k8s-owned-up k8s-up

features-test:
	uv run --directory platform/features pytest -q

features-lint:
	uv run --directory platform/features ruff check src tests feature_repo
	uv run --directory platform/features ty check src tests feature_repo
	uv run --directory platform/features basedpyright src tests feature_repo

k8s-validate:
	$(KUBECTL) apply --dry-run=server -f $(K8S_DIR)/namespaces.yaml -f $(K8S_DIR)/kafka.yaml -f $(K8S_DIR)/postgres.yaml -f $(K8S_DIR)/connect.yaml -f $(K8S_DIR)/connector-postgres.yaml
	$(HELM) template mlops-mongodb bitnami/mongodb --version 16.5.45 --namespace mlops-data -f $(K8S_DIR)/mongodb-values.yaml >/dev/null
	$(HELM) template mlops-minio minio/minio --version 5.4.0 --namespace mlops-data -f $(K8S_DIR)/minio-values.yaml >/dev/null
	$(HELM) template mlops-redis bitnami/redis --version 28.0.10 --namespace mlops-data -f $(K8S_DIR)/redis-values.yaml >/dev/null
	$(HELM) template event-counts platform/streaming/event-counts/chart --namespace mlops-streaming -f $(K8S_DIR)/event-counts-values.yaml >/dev/null
	$(HELM) template events-lake platform/streaming/events-lake/chart --namespace mlops-streaming -f $(K8S_DIR)/events-lake-values.yaml >/dev/null
	$(HELM) template gateway platform/services/event-gateway/chart --namespace mlops-gateway -f $(K8S_DIR)/gateway-values.yaml >/dev/null

k8s-operators:
	$(KUBECTL) apply -f $(K8S_DIR)/namespaces.yaml
	$(HELM) upgrade --install strimzi oci://quay.io/strimzi-helm/strimzi-kafka-operator --version 1.1.0 --namespace strimzi-system --create-namespace --set 'watchNamespaces[0]=mlops-data' --wait
	$(HELM) upgrade --install cnpg cnpg/cloudnative-pg --version 0.29.0 --namespace cnpg-system --create-namespace --wait

k8s-data-up: k8s-operators
	$(KUBECTL) apply -f $(K8S_DIR)/kafka.yaml -f $(K8S_DIR)/postgres.yaml
	$(HELM) upgrade --install mlops-mongodb bitnami/mongodb --version 16.5.45 --namespace mlops-data -f $(K8S_DIR)/mongodb-values.yaml --wait
	$(HELM) upgrade --install mlops-minio minio/minio --version 5.4.0 --namespace mlops-data -f $(K8S_DIR)/minio-values.yaml --wait
	$(HELM) upgrade --install mlops-redis bitnami/redis --version 28.0.10 --namespace mlops-data -f $(K8S_DIR)/redis-values.yaml --wait
	$(KUBECTL) apply -f $(K8S_DIR)/connect.yaml -f $(K8S_DIR)/connector-postgres.yaml

k8s-owned-up: k8s-data-up
	$(HELM) template event-counts platform/streaming/event-counts/chart --namespace mlops-streaming -f $(K8S_DIR)/event-counts-values.yaml | $(KUBECTL) apply -f -
	$(HELM) template events-lake platform/streaming/events-lake/chart --namespace mlops-streaming -f $(K8S_DIR)/events-lake-values.yaml | $(KUBECTL) apply -f -
	$(HELM) template gateway platform/services/event-gateway/chart --namespace mlops-gateway -f $(K8S_DIR)/gateway-values.yaml | $(KUBECTL) apply -f -

k8s-up: k8s-owned-up
