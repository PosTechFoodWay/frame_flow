from datetime import datetime
from pathlib import Path
from typing import Any
import aioboto3
import redis.asyncio as redis
from fastapi import UploadFile

from upload_service.config import config
from upload_service.repo import FileRepository
from uuid import uuid4
from .models import FileUploadedEvent


class UploadService:
    def __init__(
        self, file_repo: FileRepository, redis_client: redis.Redis, aws_session: aioboto3.Session
    ):
        self.file_repo = file_repo
        self.redis_client = redis_client
        self.aws_session = aws_session

    async def upload_file_to_s3(self, file: UploadFile, user_id: str) -> dict[str, Any]:
        """
        Faz upload do arquivo para S3 e retorna metadados (id, s3_path).
        Publica evento no Redis e salva metadados no Postgres.
        """
        # Gera um nome único no S3 (uuid + extensao)
        event_id = str(uuid4())
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{file_ext}"

        s3_key = f"{user_id}/{event_id}/{unique_filename}"

        async with self.aws_session.client("s3") as s3_client:
            print(f">> Uploading file to S3: {s3_key}")
            print(f">> Bucket name: {config.s3_bucket_name}")
            bucket_name = config.s3_bucket_name
            await s3_client.upload_fileobj(file.file, bucket_name, s3_key)
            s3_path = f"s3://{bucket_name}/{s3_key}"

        # Insere metadados no Postgres
        file_id = await self.file_repo.insert_file(
            filename=file.filename, s3_path=s3_path, user_id=user_id
        )

        # Publica evento no Redis
        file_uploaded_event = FileUploadedEvent(
            file_id=file_id, event_id=event_id, s3_path=s3_path, user_id=user_id
        )
        await self.redis_client.publish("saga_events", file_uploaded_event.model_dump_json())
        await self.redis_client.set(event_id, "FILE_UPLOADED")

        return {"id": file_id, "filename": file.filename, "event_id": event_id}

    async def get_upload_status(self, event_id: str) -> str:
        """
        Retorna o status do upload de um arquivo.
        """
        return await self.redis_client.get(event_id)
