import asyncio
import logging
from contextlib import asynccontextmanager

import aioboto3
import redis.asyncio as redis
from fastapi import FastAPI

from .config import config
from .models import ProcessFileEventModel
from .process import ProcessFileEvent
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def redis_listener(redis_client: redis.Redis, aws_session: aioboto3.Session):
    """Background Redis listener."""
    logger.info("Started Redis listener.")
    async with redis.Redis(
        host=config.redis_host, port=config.redis_port, db=config.redis_db, decode_responses=True
    ).pubsub() as pubsub:
        await pubsub.subscribe("process_file")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)
            if message:
                raw_message_data = message.get("data")
                try:
                    data = json.loads(raw_message_data)
                    logger.info(f"Received message: {data}")
                    event = ProcessFileEventModel(**data)
                    processor = ProcessFileEvent(redis_client, aws_session, event)
                    await processor.process()
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

            await asyncio.sleep(0.01)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Redis client...")
    r = redis.Redis(
        host=config.redis_host, port=config.redis_port, db=config.redis_db, decode_responses=True
    )
    app.state.redis_client = r
    aws_session = aioboto3.Session(
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        aws_session_token=config.aws_session_token,
        region_name=config.aws_region_name,
    )
    app.state.aws_session = aws_session

    # Start listener
    task = asyncio.create_task(redis_listener(r, aws_session))
    yield

    # Cleanup
    task.cancel()
    await r.aclose()
    logger.info("Redis client closed.")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="Process Service")
    return app


app = create_app()


@app.get("/health")
async def root():
    return {"message": "Process service is running"}
