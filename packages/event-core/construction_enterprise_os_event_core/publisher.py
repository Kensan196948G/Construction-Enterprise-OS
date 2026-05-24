import asyncio
import json
from typing import Optional
from aiokafka import AIOKafkaProducer


class EventPublisher:
    """Kafka event publisher"""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()

    async def publish(
        self, topic: str, event: dict, key: Optional[str] = None
    ):
        if not self._producer:
            raise RuntimeError("Publisher not started. Call start() first.")
        await self._producer.send_and_wait(topic, event, key=key)
