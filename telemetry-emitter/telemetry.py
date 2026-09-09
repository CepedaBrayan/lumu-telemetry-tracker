import os
import random
from datetime import datetime, timezone
from ipaddress import IPv4Address

DEVICE_COUNT = 120_000_000
BASE_IP = int(IPv4Address("10.0.0.1"))
INVALID_EVENT_RATE = float(os.getenv("INVALID_EVENT_RATE", "0.20"))


def generate_event() -> dict:
    """Generate simulated telemetry, including occasional invalid events."""

    now = datetime.now(timezone.utc)
    iso_timestamp = now.isoformat(timespec="milliseconds")
    seconds = int(now.timestamp())
    milliseconds = seconds * 1_000 + now.microsecond // 1_000

    valid_timestamps = [
        iso_timestamp.replace("+00:00", "Z"),
        iso_timestamp.removesuffix("+00:00"),
        now.strftime("%Y-%m-%d %H:%M:%S"),
        seconds,
        str(seconds),
        milliseconds,
        str(milliseconds),
    ]

    device_id = random.randrange(DEVICE_COUNT)

    event = {
        "timestamp": random.choice(valid_timestamps),
        "device_ip": str(IPv4Address(BASE_IP + device_id)),
        "error_code": random.choice([0, 1, 2, 3]),
    }

    # Return a valid event according to the configured success rate.
    if random.random() >= INVALID_EVENT_RATE:
        return event

    # Simulate malformed telemetry from outdated or damaged devices.
    invalid_case = random.choice(
        [
            "invalid_timestamp",
            "invalid_ip",
            "invalid_error_code",
            "missing_timestamp",
            "missing_device_ip",
            "missing_error_code",
        ]
    )

    if invalid_case == "invalid_timestamp":
        event["timestamp"] = random.choice(
            [
                "",
                "not-a-timestamp",
                "2026/09/09 15:30:00",
                "yesterday",
                None,
                [],
            ]
        )

    elif invalid_case == "invalid_ip":
        event["device_ip"] = random.choice(
            [
                "",
                "hola crack",
                "999.168.1.10",
                "localhost",
                "2001:db8::1",
                None,
            ]
        )

    elif invalid_case == "invalid_error_code":
        event["error_code"] = random.choice(
            [
                "unknown",
                None,
                True,
                [],
            ]
        )

    elif invalid_case == "missing_timestamp":
        event.pop("timestamp")

    elif invalid_case == "missing_device_ip":
        event.pop("device_ip")

    elif invalid_case == "missing_error_code":
        event.pop("error_code")

    return event
