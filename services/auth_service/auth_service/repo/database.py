from contextlib import asynccontextmanager

import asyncpg
from fastapi import Depends, Request


async def get_pool(request: Request) -> asyncpg.Pool:
    """Retorna o pool armazenado em app.state."""
    return request.app.state.db_pool


@asynccontextmanager
async def get_connection_from_pool(pool: asyncpg.Pool):
    """Abre e libera uma conexão do pool, como um async context manager."""
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


async def get_connection(pool: asyncpg.Pool = Depends(get_pool)):
    """
    Dependência FastAPI que faz "async with" no pool,
    yield a conexão e libera no final da requisição.
    """
    async with get_connection_from_pool(pool) as conn:
        yield conn
