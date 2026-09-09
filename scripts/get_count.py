"""
Assumptions:
- All receivers write to the same Redis set.
- This script reads Redis directly from the local machine.
- Watch mode refreshes every 0.5 seconds while Redis responds normally.
- A missing set means zero IPs; query failures are reported as errors.
[Lumu Challenge]
"""

import argparse
import os
import sys
import time
from datetime import datetime, timezone

from redis.exceptions import RedisError

from redis import Redis


def show_count(
    total: int, watch: bool
) -> None:  # Refresh the counter in place or print a single snapshot!!!
    use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    green = "\033[1;92m" if use_color else ""
    reset = "\033[0m" if use_color else ""

    checked_at = datetime.now(timezone.utc).strftime("%H:%M:%S")

    text = f"LUMU | Unique IPs: {green}{total:,}{reset}" f" | {checked_at} UTC"

    if watch:
        text += " | Refresh: 0.5s | Ctrl+C to exit"
        print(f"\r{text}    ", end="", flush=True)
    else:
        print(text)


def main() -> int:  # Query the global count once or monitor it every half second!!!
    parser = argparse.ArgumentParser(
        description="Display the global unique device IP count."
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Refresh the count every 0.5 seconds.",
    )
    args = parser.parse_args()

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_key = os.getenv("REDIS_IPS_KEY", "telemetry:unique_ips")

    try:
        with Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        ) as client:
            while True:
                started = time.monotonic()

                total = client.scard(redis_key)
                show_count(total, watch=args.watch)

                if not args.watch:
                    break

                elapsed = time.monotonic() - started
                time.sleep(max(0, 0.5 - elapsed))

    except KeyboardInterrupt:
        # guardrail: Stop monitoring cleanly when interrupted.
        print("\n  Counter stopped.")
        return 0

    except (RedisError, ValueError):
        # guardrail: Report failures instead of presenting a stale count as current.
        print(
            "\n  ERROR: Unable to retrieve the Redis count. "
            "Any previously displayed value is stale.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
