COMPOSE_FILE := platform/infra/compose.data.yaml
COMPOSE := docker compose --env-file .env -f $(COMPOSE_FILE)

.PHONY: data-preflight data-guard data-up data-health data-stats data-down

data-preflight: data-guard
	docker ps
	memory_pressure | head -20
	docker stats --no-stream

data-guard:
	@foreign=$$(docker compose ls --format '{{.Name}}' 2>/dev/null | awk '$$0 != "" && $$0 != "data" && $$0 != "cdc"'); \
	if [ -n "$$foreign" ]; then echo "refusing: active compose project(s) other than 'data'+'cdc':" $$foreign >&2; exit 1; fi

data-up: data-guard
	$(COMPOSE) config -q
	$(COMPOSE) up -d

data-health:
	docker exec data-postgres pg_isready -U $${POSTGRES_USER:-mlops}
	docker exec data-mongodb mongosh --quiet --eval "db.adminCommand('ping').ok"
	docker exec data-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list >/dev/null && echo "kafka: topics listable"
	docker exec data-minio mc ready local && echo "minio: ready"

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
