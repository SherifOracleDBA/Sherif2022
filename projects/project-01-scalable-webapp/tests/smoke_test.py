"""Smoke test a deployed Project 01 URL without third-party dependencies."""

import argparse
import json
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def check_health(base_url: str, attempts: int, delay: float) -> bool:
    url = base_url.rstrip("/") + "/health"
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(url, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if response.status == 200 and payload.get("status") == "ok":
                    print(f"PASS: {url} returned healthy")
                    return True
                print(f"Unexpected response from {url}: {response.status} {payload}")
        except (URLError, TimeoutError, ValueError) as exc:
            print(f"Attempt {attempt}/{attempts} failed: {exc}")
        if attempt < attempts:
            time.sleep(delay)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="CloudFront distribution or custom hostname")
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--delay", type=float, default=15)
    args = parser.parse_args()

    return 0 if check_health(args.url, args.attempts, args.delay) else 1


if __name__ == "__main__":
    sys.exit(main())
