# download_service/main.py

from contextlib import asynccontextmanager

import aioboto3
import redis.asyncio as redis
from fastapi import FastAPI

from .config import config
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        decode_responses=True,
    )
    app.state.redis_client = r

    aws_session = aioboto3.Session(
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        aws_session_token=config.aws_session_token,
        region_name=config.aws_region_name,
    )
    app.state.aws_session = aws_session

    print(">> Startup: created db_pool, redis async client, and AWS session.")

    yield

    await r.aclose()
    print(">> Shutdown: closed db_pool and redis client.")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="Download Service", debug=True)

    app.include_router(router, tags=["download"])

    return app


app = create_app()
