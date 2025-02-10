from .interface import IEventHandler
from orchestrator.models import BaseEvent
import logging

logger = logging.getLogger(__name__)


class FileProcessedHandler(IEventHandler):
    async def handle(self, event: BaseEvent):
        await self.redis_client.set(event.event_id, "FILE_PROCESSED")
