"""
Assumptions:
- All receiver instances use the same Kafka consumer group.
- Timestamps without a timezone are interpreted as UTC.
- Numeric timestamps with absolute value >= 100 billion use milliseconds;
  smaller values use seconds. This heuristic covers the supplied examples.
- error_code must be a finite JSON number.
- Invalid events are logged and skipped.
- Valid device IPs are stored in a shared Redis set.
- Redis failures propagate and prevent committing the current event.
- Offsets are committed after handling, allowing replay after a crash.
- Redis persistence is disabled in the current local configuration.
[Lumu Challenge]
"""

import logging
import os
import socket
from functools import partial

from consumer import KafkaReceiver
from redis_store import connect_redis, count_unique_ips, register_ip
from utils import validate_event

from redis import Redis

logger = logging.getLogger(__name__)


def handle_event(
    payload: bytes | None, *, redis_client: Redis, redis_key: str
) -> None:  # Validate telemetry and update the shared unique IP set!!!
    if payload is None:
        logger.warning("Skipped event: empty Kafka value")
        return

    try:
        event = validate_event(payload)
    except (ValueError, OverflowError, RecursionError) as error:
        # guardrail: Skip invalid telemetry without updating Redis.
        logger.warning("Skipped event: %s", error)
        return

    is_new = register_ip(redis_client, redis_key, event["device_ip"])

    logger.info(
        "Accepted timestamp=%s device_ip=%s error_code=%s " "new_ip=%s",
        event["timestamp"].isoformat(),
        event["device_ip"],
        event["error_code"],
        is_new,
    )


def main() -> None:  # Initialize connections and run the telemetry receiver!!!
    node = socket.gethostname()

    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s %(levelname)s node={node} %(message)s",
    )

    redis_client = connect_redis(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    try:
        receiver = KafkaReceiver(
            broker=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            topic=os.getenv("KAFKA_TOPIC", "telemetry.events"),
            group=os.getenv("KAFKA_GROUP_ID", "telemetry-receptors"),
        )

        handler = partial(
            handle_event,
            redis_client=redis_client,
            redis_key=os.getenv("REDIS_IPS_KEY", "telemetry:unique_ips"),
        )

        receiver.run(handler)

    except KeyboardInterrupt:
        # guardrail: Allow a clean manual shutdown.
        logger.info("Receiver stopped")

    finally:
        redis_client.close()


if __name__ == "__main__":
    main()
