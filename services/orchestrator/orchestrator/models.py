from typing import Optional
from pydantic import BaseModel, Field, field_validator
import json

from enum import StrEnum


class SagaEventTypes(StrEnum):
    FILE_UPLOADED = "FILE_UPLOADED"
    FILE_PROCESSED = "FILE_PROCESSED"
    FILE_FAILED = "FILE_FAILED"


class BaseEvent(BaseModel):
    event_id: str = Field(..., description="Unique event ID")
    event_type: SagaEventTypes = Field(..., description="Type of the event")
    user_id: str = Field(..., description="User ID related to the event")
    s3_path: Optional[str] = None

    @field_validator("event_type")
    def validate_event_type(cls, value):
        allowed_types = {"FILE_UPLOADED", "FILE_PROCESSED", "FILE_FAILED"}
        if value not in allowed_types:
            raise ValueError(f"Invalid event type: {value}")
        return value

    @classmethod
    def from_redis_message(cls, raw_message: bytes) -> "BaseEvent":
        try:
            decoded_str = raw_message.decode("utf-8")
            json_data = json.loads(decoded_str)
            return cls(**json_data)
        except Exception as e:
            raise ValueError(f"Error parsing event: {e}")
