from datetime import datetime
from uuid import uuid4

import asyncpg


class FileRepository:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def insert_file(self, filename: str, s3_path: str, user_id: str) -> str:
        file_id = str(uuid4())
        await self.conn.execute(
            """
            INSERT INTO files (id, filename, s3_path, uploaded_at, user_id)
            VALUES ($1, $2, $3, $4, $5)
            """,
            file_id,
            filename,
            s3_path,
            datetime.now(),
            user_id,
        )
        return file_id
