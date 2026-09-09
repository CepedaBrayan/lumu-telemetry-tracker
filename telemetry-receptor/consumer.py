import logging
import socket
from collections.abc import Callable

from confluent_kafka import Consumer, KafkaException

logger = logging.getLogger(__name__)


class KafkaReceiver:
    def __init__(
        self, broker: str, topic: str, group: str
    ):  # Configure the Kafka consumer instance!!!
        self.topic = topic
        self._consumer = Consumer(
            {
                "bootstrap.servers": broker,
                "group.id": group,
                "client.id": f"telemetry-receptor-{socket.gethostname()}",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
                "enable.auto.offset.store": False,
            }
        )

    def run(
        self, handler: Callable[[bytes | None], None]
    ) -> None:  # Consume messages and commit only after handling!!!
        try:
            self._consumer.subscribe([self.topic])
            logger.info("Listening on topic=%s", self.topic)

            while True:
                message = self._consumer.poll(1.0)

                if message is None:
                    continue

                if message.error():
                    raise KafkaException(message.error())

                logger.debug(
                    "Received partition=%s offset=%s",
                    message.partition(),
                    message.offset(),
                )

                handler(message.value())

                # Invalid events are also committed once logged and skipped.
                self._consumer.commit(
                    message=message,
                    asynchronous=False,
                )
        finally:
            self._consumer.close()
