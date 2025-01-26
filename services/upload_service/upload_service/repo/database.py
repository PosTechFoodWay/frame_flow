from contextlib import asynccontextmanager

import asyncpg
from fastapi import Request


async def get_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool


@asynccontextmanager
async def get_connection(pool: asyncpg.Pool):
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)
