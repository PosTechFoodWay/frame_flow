from orchestrator.models import BaseEvent
from abc import ABC, abstractmethod
from redis.asyncio import Redis


class IEventHandler(ABC):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    @abstractmethod
    async def handle(self, event: BaseEvent) -> None:
        pass
