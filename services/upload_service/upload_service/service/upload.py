from datetime import datetime
import json
from pathlib import Path
from typing import Any
import aioboto3
import redis.asyncio as redis
from fastapi import UploadFile

from upload_service.config import config
from upload_service.repo import FileRepository
from uuid import uuid4


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
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{file_ext}"

        s3_key = f"{user_id}/{unique_filename}"

        async with self.aws_session.client("s3") as s3_client:
            bucket_name = config.s3_bucket_name
            await s3_client.upload_fileobj(file.file, bucket_name, s3_key)
            s3_path = f"s3://{bucket_name}/{s3_key}"

        # Insere metadados no Postgres
        file_id = await self.file_repo.insert_file(
            filename=file.filename, s3_path=s3_path, user_id=user_id
        )

        # Publica evento no Redis
        event_id = str(uuid4())
        event_data = {"id": file_id, "s3_path": s3_path, "user_id": user_id, "event_id": event_id}
        await self.redis_client.publish("saga_events", json.dumps(event_data))

        return {"id": file_id, "filename": file.filename}
