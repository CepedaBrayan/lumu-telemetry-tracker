import random
from datetime import datetime, timezone
from ipaddress import IPv4Address


DEVICE_COUNT = 100_000_000
BASE_IP = int(IPv4Address("10.0.0.1"))


def generate_event() -> dict:  # Generate a valid simulated telemetry event!!!
    now = datetime.now(timezone.utc)
    iso = now.isoformat(timespec="milliseconds")
    seconds = int(now.timestamp())
    milliseconds = seconds * 1_000 + now.microsecond // 1_000

    timestamp = random.choice([
        iso.replace("+00:00", "Z"),
        iso.removesuffix("+00:00"),
        now.strftime("%Y-%m-%d %H:%M:%S"),
        seconds,
        str(seconds),
        milliseconds,
        str(milliseconds),
    ])

    device_id = random.randrange(DEVICE_COUNT)

    return {
        "timestamp": timestamp,
        "device_ip": str(IPv4Address(BASE_IP + device_id)),
        "error_code": random.choice([0, 1, 2, 3]),
    }