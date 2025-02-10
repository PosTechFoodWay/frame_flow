from pydantic import BaseModel


class BaseEvent(BaseModel):
    event_id: str
    event_type: str
    user_id: str
    s3_path: str | None = None


class ProcessFileEventModel(BaseModel):
    event_id: str
    event_type: str = "PROCESS_FILE"
    user_id: str
    s3_path: str


class FileProcessedEvent(BaseEvent):
    s3_path: str
    event_type: str = "FILE_PROCESSED"
