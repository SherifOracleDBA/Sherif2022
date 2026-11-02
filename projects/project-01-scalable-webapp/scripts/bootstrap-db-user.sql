-- Run as the RDS master user through an SSM port-forward.
-- Credentials are passed through the process environment, not SQL arguments.

\getenv app_username APP_DB_USERNAME
\getenv app_password APP_DB_PASSWORD
\getenv db_name APP_DB_NAME

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'app_username', :'app_password')
WHERE NOT EXISTS (
  SELECT 1 FROM pg_roles WHERE rolname = :'app_username'
) \gexec

SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'app_username', :'app_password') \gexec

GRANT CONNECT ON DATABASE :"db_name" TO :"app_username";
CREATE SCHEMA IF NOT EXISTS app;
GRANT USAGE ON SCHEMA app TO :"app_username";

CREATE TABLE IF NOT EXISTS app.visits (
  id BIGSERIAL PRIMARY KEY,
  visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

GRANT SELECT, INSERT ON TABLE app.visits TO :"app_username";
GRANT USAGE, SELECT ON SEQUENCE app.visits_id_seq TO :"app_username";
ALTER DEFAULT PRIVILEGES IN SCHEMA app
  GRANT SELECT, INSERT ON TABLES TO :"app_username";
