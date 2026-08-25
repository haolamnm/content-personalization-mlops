#!/usr/bin/env bash
# Register the Postgres CDC connector against a running Debezium Connect (data group + cdc slice up).
# Reads credentials from root .env; connector targets postgres over the shared mlops-data network.
set -euo pipefail

cd "$(dirname "$0")/../../.."
[ -f .env ] || { echo "missing .env — copy .env.example first" >&2; exit 1; }
set -a; . .env; set +a

CONNECT_URL="http://localhost:${CONNECT_HOST_PORT:-8083}"

body=$(curl -sf -X POST "$CONNECT_URL/connectors" \
  -H 'Content-Type: application/json' \
  -d @- <<JSON
{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "${POSTGRES_USER}",
    "database.password": "${POSTGRES_PASSWORD}",
    "database.dbname": "${POSTGRES_DB}",
    "topic.prefix": "mlops",
    "table.include.list": "public.interactions",
    "plugin.name": "pgoutput",
    "slot.name": "mlops_cdc",
    "publication.name": "mlops_pub",
    "publication.autocreate.mode": "filtered",
    "schema.history.internal.kafka.topic": "cdc-schema-history-postgres"
  }
}
JSON
) || { echo "registration POST failed" >&2; exit 1; }
printf '%s' "$body" | head -c 400; echo

echo "connector registered — status:"
curl -s "$CONNECT_URL/connectors/postgres-source/status" | head -c 400; echo
