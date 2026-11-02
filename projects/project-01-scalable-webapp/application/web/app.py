"""Web application for the AWS scalable web app assessment lab."""

from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlsplit


def route_response(path: str) -> tuple[int, str, str]:
    """Return (status, body, content_type) for non-database GET routes."""
    if path == "/health":
        return 200, json.dumps({"status": "ok"}), "application/json"
    if path == "/":
        body = (
            "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<title>AWS Scalable Web App</title>"
            "<link rel='stylesheet' href='/static/style.css'></head><body>"
            "<main><h1>AWS Scalable Web Application</h1>"
            "<p>Served by an EC2 instance in a private subnet.</p>"
            "<p>Use <code>/database</code> to check PostgreSQL connectivity "
            "and send POST requests to <code>/visits</code> to write a visit.</p>"
            "</main></body></html>"
        )
        return 200, body, "text/html; charset=utf-8"
    if path == "/static/style.css":
        return (
            200,
            "body{font-family:system-ui,sans-serif;margin:3rem;background:#f5f7fb}"
            "main{max-width:48rem;margin:auto;padding:2rem;background:white;"
            "border-radius:1rem}h1{color:#172b4d}",
            "text/css; charset=utf-8",
        )
    return 404, json.dumps({"error": "not_found"}), "application/json"


@lru_cache(maxsize=1)
def database_credentials() -> dict:
    """Read and cache the app-only database secret from Secrets Manager."""
    secret_arn = os.getenv("DB_SECRET_ARN")
    if not secret_arn:
        raise RuntimeError("DB_SECRET_ARN is not configured")

    import boto3

    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_arn)
    secret_string = response.get("SecretString")
    if not secret_string:
        raise RuntimeError("Database secret has no SecretString")
    return json.loads(secret_string)


def get_database_connection():
    """Open an encrypted PostgreSQL connection using the least-privilege app user."""
    import psycopg

    credentials = database_credentials()
    return psycopg.connect(
        host=credentials["host"],
        port=int(credentials.get("port", 5432)),
        dbname=credentials["dbname"],
        user=credentials["username"],
        password=credentials["password"],
        connect_timeout=5,
        sslmode="require",
    )


def database_health() -> dict:
    """Return a small database connectivity result."""
    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), NOW()")
            row = cursor.fetchone()
    return {
        "status": "ok",
        "database": row[0],
        "server_time": row[1].isoformat(),
    }


def create_visit() -> dict:
    """Insert one non-personal demo visit and return its generated identifier."""
    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO app.visits DEFAULT VALUES RETURNING id")
            visit_id = cursor.fetchone()[0]
    return {"status": "created", "visit_id": visit_id}


def database_api_response(path: str, method: str):
    """Handle database-backed routes; return None for routes handled elsewhere."""
    if path == "/database" and method == "GET":
        try:
            return 200, json.dumps(database_health()), "application/json"
        except Exception:
            return (
                503,
                json.dumps({"status": "error", "message": "Database unavailable"}),
                "application/json",
            )
    if path == "/visits" and method == "POST":
        try:
            return 201, json.dumps(create_visit()), "application/json"
        except Exception:
            return (
                503,
                json.dumps({"status": "error", "message": "Database write unavailable"}),
                "application/json",
            )
    return None


class PortfolioRequestHandler(BaseHTTPRequestHandler):
    server_version = "PortfolioDemo/1.1"

    def _send_payload(self, path: str, result: tuple[int, str, str]) -> None:
        status, body, content_type = result
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        cache_control = (
            "public, max-age=86400"
            if path == "/static/style.css"
            else "no-store"
        )
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlsplit(self.path).path
        result = database_api_response(path, "GET")
        self._send_payload(path, result if result is not None else route_response(path))

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlsplit(self.path).path
        result = database_api_response(path, "POST")
        self._send_payload(
            path,
            result if result is not None else (404, json.dumps({"error": "not_found"}), "application/json"),
        )

    def log_message(self, fmt: str, *args: object) -> None:
        # Do not log query strings, which may contain tokens or other sensitive values.
        return


def main() -> None:
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), PortfolioRequestHandler)
    print(f"Portfolio demo listening on {host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
