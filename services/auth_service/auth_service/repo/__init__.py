import asyncpg
from fastapi import Depends

from .database import get_connection
from .user_repo import UserRepository


async def get_user_repository(conn: asyncpg.Connection = Depends(get_connection)):
    return UserRepository(conn)


__all__ = ["get_user_repository", "UserRepository"]
