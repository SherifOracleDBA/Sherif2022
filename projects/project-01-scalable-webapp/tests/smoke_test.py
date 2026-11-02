"""Smoke-test the deployed Project 01 app and optional DB integration."""

import argparse
import json
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


def request_json(url: str, method: str = "GET", attempts: int = 1, delay: float = 0):
    request = Request(url, data=b"" if method == "POST" else None, method=method)
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status, payload
        except (URLError, TimeoutError, ValueError) as exc:
            print(f"Attempt {attempt}/{attempts} failed for {url}: {exc}")
            if attempt < attempts:
                time.sleep(delay)
    return None, None


def check_health(base_url: str, attempts: int, delay: float) -> bool:
    url = base_url.rstrip("/") + "/health"
    status, payload = request_json(url, attempts=attempts, delay=delay)
    if status == 200 and payload and payload.get("status") == "ok":
        print(f"PASS: {url} returned healthy")
        return True
    print(f"FAIL: {url} did not return a healthy response")
    return False


def check_database(base_url: str) -> bool:
    url = base_url.rstrip("/") + "/database"
    status, payload = request_json(url)
    if status == 200 and payload and payload.get("status") == "ok":
        print(f"PASS: PostgreSQL connectivity verified ({payload.get('database')})")
        return True
    print(f"FAIL: database health check did not pass (HTTP {status})")
    return False


def create_visit(base_url: str) -> bool:
    url = base_url.rstrip("/") + "/visits"
    status, payload = request_json(url, method="POST")
    if status == 201 and payload and payload.get("status") == "created":
        print(f"PASS: database write succeeded (visit id {payload.get('visit_id')})")
        return True
    print(f"FAIL: database write did not pass (HTTP {status})")
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="CloudFront application URL")
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--delay", type=float, default=15)
    parser.add_argument("--check-database", action="store_true", help="Verify PostgreSQL connectivity")
    parser.add_argument("--create-visit", action="store_true", help="Insert a demo row into app.visits")
    args = parser.parse_args()

    passed = check_health(args.url, args.attempts, args.delay)
    if args.check_database or args.create_visit:
        passed = check_database(args.url) and passed
    if args.create_visit:
        passed = create_visit(args.url) and passed
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
