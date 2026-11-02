#!/usr/bin/env bash
set -Eeuo pipefail

: "${AWS_REGION:?Set AWS_REGION, for example us-east-1}"
: "${MASTER_SECRET_ARN:?Set MASTER_SECRET_ARN from terraform output}"
: "${APP_SECRET_ARN:?Set APP_SECRET_ARN from terraform output}"

LOCAL_DB_PORT="${LOCAL_DB_PORT:-15432}"

for command_name in aws jq psql; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Required command not found: $command_name" >&2
    exit 1
  fi
done

MASTER_SECRET_JSON="$(aws secretsmanager get-secret-value \
  --region "$AWS_REGION" \
  --secret-id "$MASTER_SECRET_ARN" \
  --query SecretString \
  --output text)"

APP_SECRET_JSON="$(aws secretsmanager get-secret-value \
  --region "$AWS_REGION" \
  --secret-id "$APP_SECRET_ARN" \
  --query SecretString \
  --output text)"

export PGHOST="127.0.0.1"
export PGPORT="$LOCAL_DB_PORT"
export PGSSLMODE="require"
export PGUSER="$(jq -er '.username' <<<"$MASTER_SECRET_JSON")"
export PGPASSWORD="$(jq -er '.password' <<<"$MASTER_SECRET_JSON")"
export PGDATABASE="$(jq -er '.dbname' <<<"$APP_SECRET_JSON")"

export APP_DB_USERNAME="$(jq -er '.username' <<<"$APP_SECRET_JSON")"
export APP_DB_PASSWORD="$(jq -er '.password' <<<"$APP_SECRET_JSON")"
export APP_DB_NAME="$PGDATABASE"

cleanup() {
  unset PGPASSWORD APP_DB_PASSWORD MASTER_SECRET_JSON APP_SECRET_JSON
}
trap cleanup EXIT

echo "Connecting through the local SSM port-forward on 127.0.0.1:$LOCAL_DB_PORT ..."
psql --no-password --set ON_ERROR_STOP=1 \
  --file="$(dirname "$0")/bootstrap-db-user.sql"

echo "Database app role and app.visits table are ready."
