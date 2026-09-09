"""
Assumptions:
- Kafka already has a topic with exactly three partitions.
- Target emission rate is 300 events per second, not a real-time guarantee.
- Events use valid timestamps and a pool of 1,000 simulated IPv4 devices.
- Repeated device IPs are intentional.
- Events are distributed round-robin across the three partitions.
[Lumu Challenge]
"""

import logging
import os
import time

from publisher import KafkaPublisher
from telemetry import generate_event


EVENTS_PER_SECOND = 300
PARTITIONS = 3
REPORT_INTERVAL_SECONDS = 5

logger = logging.getLogger(__name__)


def main() -> None:  # Coordinate telemetry generation and rate-controlled publishing!!!
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    publisher = KafkaPublisher(
        broker=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        topic=os.getenv("KAFKA_TOPIC", "telemetry.events"),
        partitions=PARTITIONS,
    )

    interval = 1 / EVENTS_PER_SECOND
    next_send = time.monotonic()
    next_report = next_send + REPORT_INTERVAL_SECONDS

    logger.info(
        "Emitter started: target=%s events/s partitions=%s",
        EVENTS_PER_SECOND,
        PARTITIONS,
    )

    try:
        while True:
            delay = next_send - time.monotonic()
            if delay > 0:
                time.sleep(delay)

            started = time.monotonic()
            publisher.publish(generate_event())

            # Reschedule from the actual start to avoid catch-up bursts.
            next_send = started + interval

            current = time.monotonic()
            if current >= next_report:
                logger.info(
                    "Queued=%s delivered=%s failed=%s",
                    publisher.queued,
                    publisher.delivered,
                    publisher.failed,
                )
                next_report = current + REPORT_INTERVAL_SECONDS

    except KeyboardInterrupt:
        # guardrail: Stop gracefully when the user interrupts execution.
        logger.info("Stopping emitter")
    finally:
        publisher.close()


if __name__ == "__main__":
    main()