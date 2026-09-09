import json
import math
import re
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

ISO_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}" r"(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})?"
)


def parse_timestamp(
    value,
) -> datetime:  # Normalize supported timestamps into an aware UTC datetime!!!
    if isinstance(value, bool):
        raise ValueError("Invalid timestamp type")

    if isinstance(value, str):
        value = value.strip()

        if re.fullmatch(r"-?\d+", value):
            value = int(value)
        else:
            if not ISO_PATTERN.fullmatch(value):
                raise ValueError("Unsupported timestamp format")

            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Timestamp must be finite")

        # Documented heuristic: large epoch values represent milliseconds.
        if abs(value) >= 100_000_000_000:
            return EPOCH + timedelta(milliseconds=value)

        return EPOCH + timedelta(seconds=value)

    raise ValueError("Unsupported timestamp type")


def validate_event(
    payload: bytes,
) -> dict:  # Decode and validate the incoming telemetry payload!!!
    event = json.loads(payload.decode("utf-8"))

    if not isinstance(event, dict):
        raise ValueError("Event must be a JSON object")

    required = {"timestamp", "device_ip", "error_code"}
    missing = required - event.keys()

    if missing:
        raise ValueError(f"Missing fields: {', '.join(sorted(missing))}")

    if not isinstance(event["device_ip"], str):
        raise ValueError("device_ip must be a string")

    ip = IPv4Address(event["device_ip"])
    timestamp = parse_timestamp(event["timestamp"])
    error_code = event["error_code"]

    if (
        isinstance(error_code, bool)
        or not isinstance(error_code, (int, float))
        or (isinstance(error_code, float) and not math.isfinite(error_code))
    ):
        raise ValueError("error_code must be a finite number")

    return {
        "timestamp": timestamp,
        "device_ip": str(ip),
        "error_code": error_code,
    }
