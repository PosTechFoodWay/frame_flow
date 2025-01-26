from datetime import datetime
from typing import Optional
from uuid import UUID

import asyncpg


class UserRepository:
    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn

    async def create_user(self, email: str, password_hash: str) -> UUID:
        row = await self._conn.fetchrow(
            """
            INSERT INTO users (id, email, password_hash, created_at)
            VALUES (gen_random_uuid(), $1, $2, $3)
            RETURNING id
            """,
            email,
            password_hash,
            datetime.now(),
        )
        return row["id"]

    async def get_user_by_email(self, email: str) -> Optional[asyncpg.Record]:
        row = await self._conn.fetchrow(
            """
            SELECT id, email, password_hash, created_at
            FROM users
            WHERE email = $1
            """,
            email,
        )
        return row

    async def user_exists(self, email: str) -> bool:
        row = await self._conn.fetchrow("SELECT 1 FROM users WHERE email = $1", email)
        return row is not None
