import json
import asyncio
import logging
from typing import Callable, Optional
from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class EventSubscriber:
    """Kafka event subscriber"""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "construction-enterprise-os-default",
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._handlers: dict[str, Callable] = {}
        self._running = False

    def register_handler(self, event_type: str, handler: Callable):
        self._handlers[event_type] = handler

    async def start(self, topics: list[str]):
        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
        )
        await self._consumer.start()
        self._running = True
        asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        while self._running:
            try:
                async for msg in self._consumer:
                    event = msg.value
                    event_type = event.get("type", "")
                    handler = self._handlers.get(event_type)
                    if handler:
                        try:
                            await handler(event)
                        except Exception as e:
                            logger.error(
                                "Error handling event %s: %s", event_type, e
                            )
            except Exception as e:
                logger.error("Consumer error: %s. Reconnecting...", e)
                await asyncio.sleep(5)

    async def stop(self):
        self._running = False
        if self._consumer:
            await self._consumer.stop()
