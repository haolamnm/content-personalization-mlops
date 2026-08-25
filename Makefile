COMPOSE_FILE := platform/infra/compose.data.yaml
COMPOSE := docker compose --env-file .env -f $(COMPOSE_FILE)

.PHONY: data-preflight data-guard data-up data-health data-stats data-down

data-preflight: data-guard
	docker ps
	memory_pressure | head -20
	docker stats --no-stream

data-guard:
	@foreign=$$(docker compose ls --format '{{.Name}}' 2>/dev/null | awk '$$0 != "" && $$0 != "data"'); \
	if [ -n "$$foreign" ]; then echo "refusing: active compose project(s) other than 'data':" $$foreign >&2; exit 1; fi

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

data-down:
	$(COMPOSE) down
