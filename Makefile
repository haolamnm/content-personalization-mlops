COMPOSE_FILE := platform/infra/compose.data.yaml
COMPOSE := docker compose --env-file .env -f $(COMPOSE_FILE)

.PHONY: data-preflight data-up data-health data-stats data-down

data-preflight:
	docker ps
	memory_pressure | head -20
	docker stats --no-stream

data-up:
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
