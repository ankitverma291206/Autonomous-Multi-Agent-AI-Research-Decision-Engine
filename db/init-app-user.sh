#!/bin/sh
set -eu

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=app_password="$APP_DB_PASSWORD" <<'SQL'
CREATE ROLE research_app LOGIN PASSWORD :'app_password';
GRANT CONNECT ON DATABASE research TO research_app;
GRANT USAGE, CREATE ON SCHEMA public TO research_app;
SQL
