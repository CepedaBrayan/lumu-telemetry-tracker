import logging

from redis import Redis

logger = logging.getLogger(__name__)


def connect_redis(
    url: str,
) -> Redis:  # Create and verify the shared Redis connection!!!
    client = Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )

    try:
        client.ping()
    except Exception:
        # guardrail: Release resources and propagate connection failures.
        client.close()
        raise

    logger.info("Redis connection established")
    return client

def register_ip(client: Redis, key: str, ip: str) -> bool:  # Atomically register an IP and report whether it is new!!!
    return client.sadd(key, ip) == 1
