from .models import BaseEvent
from .handlers import IEventHandler, FileUploadedHandler
from redis.asyncio import Redis
from .models import SagaEventTypes


class EventOrchestrator:
    def __init__(self, redis_client: Redis):
        self._handlers = {
            SagaEventTypes.FILE_UPLOADED: FileUploadedHandler(redis_client),
        }
        self._redis_client = redis_client

    async def process(self, event: BaseEvent) -> None:
        handler: IEventHandler = self._handlers.get(event.event_type)
        if not handler:
            raise ValueError(f"No handler for event type: {event.event_type}")

        await handler.handle(event)
