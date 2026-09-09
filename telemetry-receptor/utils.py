import json
import math
import re
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

ISO_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}" r"(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})?"
)


def parse_timestamp(value) -> datetime:
    """Normalize a supported timestamp into an aware UTC datetime."""

    # Just accept numbers and strings - avoid bools bc they inherit from int
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("Unsupported timestamp type")

    # Handle strings
    if isinstance(value, str):
        value = value.strip()

        if not re.fullmatch(r"-?\d+(?:\.\d+)?", value):  # if the str isn't a num inside
            if not ISO_PATTERN.fullmatch(value):  # if the string is not in ISO format
                raise ValueError("Unsupported timestamp format")

            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))

            # Assume UTC when no timezone was provided.
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            return timestamp.astimezone(timezone.utc)

    # From here, values are numbers
    numeric_value = float(value)

    # Reject NaN and positive or negative infinity.
    if not math.isfinite(numeric_value):
        raise ValueError("Timestamp must be finite")

    # Interpret large epoch values as milliseconds.
    if abs(numeric_value) >= 100_000_000_000:
        numeric_value /= 1_000

    return EPOCH + timedelta(seconds=numeric_value)


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
