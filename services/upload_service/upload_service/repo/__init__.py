import asyncpg
from fastapi import Depends

from .database import get_connection, get_pool
from .file_repo import FileRepository


async def get_file_repo(pool: asyncpg.Pool = Depends(get_pool)):
    async with get_connection(pool) as conn:
        yield FileRepository(conn)


__all__ = ["get_file_repo", "FileRepository"]
