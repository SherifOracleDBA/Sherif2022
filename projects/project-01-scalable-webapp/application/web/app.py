"""Minimal dependency-free web application for the AWS portfolio lab."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlsplit


def route_response(path: str) -> tuple[int, str, str]:
    """Return (status, body, content_type) for a URL path."""
    if path == "/health":
        return 200, json.dumps({"status": "ok"}), "application/json"
    if path == "/":
        body = (
            "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<title>AWS Scalable Web App</title>"
            "<link rel='stylesheet' href='/static/style.css'></head><body>"
            "<main><h1>AWS Scalable Web Application</h1>"
            "<p>Served by an EC2 instance in a private subnet.</p></main>"
            "</body></html>"
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


class PortfolioRequestHandler(BaseHTTPRequestHandler):
    server_version = "PortfolioDemo/1.0"

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlsplit(self.path).path
        status, body, content_type = route_response(path)
        payload = body.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        cache_control = "public, max-age=86400" if path.startswith("/static/") else "no-store"
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt: str, *args: object) -> None:
        # Avoid logging headers, tokens, or request bodies.
        super().log_message(fmt, *args)


def main() -> None:
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), PortfolioRequestHandler)
    print(f"Portfolio demo listening on {host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
