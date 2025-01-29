from pydantic import BaseModel


class BaseEvent(BaseModel):
    event_id: str
    event_type: str
    user_id: str
    s3_path: str | None = None


class FileUploadedEvent(BaseEvent):
    s3_path: str
    event_type: str = "FILE_UPLOADED"
