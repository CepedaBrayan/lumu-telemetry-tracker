import json
import logging

from confluent_kafka import Producer


logger = logging.getLogger(__name__)


class KafkaPublisher:
    def __init__(self, broker: str, topic: str, partitions: int = 3):  # Initialize and validate the Kafka publisher!!!
        self.topic = topic
        self.partitions = partitions
        self.queued = 0
        self.delivered = 0
        self.failed = 0

        self._producer = Producer({
            "bootstrap.servers": broker,
            "client.id": "telemetry-emitter",
            "enable.idempotence": True,
            "acks": "all",
            "delivery.timeout.ms": 30_000,
        })

        metadata = self._producer.list_topics(topic, timeout=10)
        topic_metadata = metadata.topics.get(topic)

        if (
            topic_metadata is None
            or topic_metadata.error
            or len(topic_metadata.partitions) != partitions
        ):
            raise RuntimeError(
                f"Topic {topic!r} must exist with {partitions} partitions"
            )

    def _on_delivery(self, error, message) -> None:  # Record broker delivery results!!!
        if error is not None:
            self.failed += 1
            logger.error("Delivery failed: %s", error)
        else:
            self.delivered += 1

    def _check_delivery_errors(self) -> None:  # Stop publishing after a confirmed delivery failure!!!
        if self.failed:
            raise RuntimeError(
                f"{self.failed} event deliveries failed"
            )

    def publish(self, event: dict) -> None:  # Serialize and enqueue an event using round-robin routing!!!
        payload = json.dumps(
            event,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

        self._producer.poll(0)
        self._check_delivery_errors()

        while True:
            try:
                self._producer.produce(
                    topic=self.topic,
                    partition=self.queued % self.partitions,
                    value=payload,
                    on_delivery=self._on_delivery,
                )
                break
            except BufferError:
                # guardrail: Wait for capacity without dropping the current event.
                self._producer.poll(0.1)
                self._check_delivery_errors()

        self.queued += 1
        self._producer.poll(0)
        self._check_delivery_errors()

    def close(self) -> None:  # Flush pending events and verify final delivery status!!!
        remaining = self._producer.flush(10)

        logger.info(
            "Final: queued=%s delivered=%s failed=%s pending=%s",
            self.queued,
            self.delivered,
            self.failed,
            remaining,
        )

        if remaining or self.failed:
            raise RuntimeError(
                f"Incomplete delivery: {remaining} pending, "
                f"{self.failed} failed"
            )