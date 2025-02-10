from .interface import IEventHandler
from orchestrator.models import BaseEvent
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProcessFileEvent(BaseModel):
    event_id: str
    event_type: str
    user_id: str
    s3_path: str


class FileUploadedHandler(IEventHandler):
    async def handle(self, event: BaseEvent):
        logger.info("Handling file uploaded event")
        process_file_event = ProcessFileEvent(
            event_id=event.event_id,
            event_type="PROCESS_FILE",
            user_id=event.user_id,
            s3_path=event.s3_path,
        )
        logging.info(f"Sending process file event: {process_file_event.model_dump_json()}")
        await self.redis_client.publish("process_file", process_file_event.model_dump_json())
        await self.redis_client.set(event.event_id, "SENT_TO_FILE_PROCESSING")
