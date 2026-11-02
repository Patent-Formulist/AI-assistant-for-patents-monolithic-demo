#!/bin/sh
# Create Temporal databases and apply/upgrade their schemas. Safe to run on every start.
set -eu
export SQL_PLUGIN=postgres12 SQL_HOST="${POSTGRES_HOST}" SQL_PORT="${POSTGRES_PORT:-5432}" \
       SQL_USER="${POSTGRES_USER}" SQL_PASSWORD="${POSTGRES_PASSWORD}"
SCHEMA=/etc/temporal/schema/postgresql/v12

for db in "${TEMPORAL_DB:-temporal}" "${TEMPORAL_VISIBILITY_DB:-temporal_visibility}"; do
  temporal-sql-tool --db "$db" create-database 2>/dev/null && echo "created database $db" || echo "database $db exists"
done

temporal-sql-tool --db "${TEMPORAL_DB:-temporal}" setup-schema -v 0.0 2>/dev/null || true
temporal-sql-tool --db "${TEMPORAL_DB:-temporal}" update-schema -d "$SCHEMA/temporal/versioned"
temporal-sql-tool --db "${TEMPORAL_VISIBILITY_DB:-temporal_visibility}" setup-schema -v 0.0 2>/dev/null || true
temporal-sql-tool --db "${TEMPORAL_VISIBILITY_DB:-temporal_visibility}" update-schema -d "$SCHEMA/visibility/versioned"
echo "temporal schemas are up to date"
