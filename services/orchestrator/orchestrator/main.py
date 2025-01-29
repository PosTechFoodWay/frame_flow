from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import redis.asyncio as redis
from .config import config
import logging
from .models import BaseEvent
from .event_orchestrator import EventOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def redis_listener(redis_client: redis.Redis):
    """Background Redis listener."""
    logger.info("Started Redis listener.")
    async with redis.Redis(
        host=config.redis_host, port=config.redis_port, db=config.redis_db
    ).pubsub() as pubsub:
        await pubsub.subscribe("saga_events")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                raw_message_data = message.get("data")
                if isinstance(raw_message_data, bytes):
                    try:
                        message_data = BaseEvent.from_redis_message(raw_message_data)
                        logger.info(f"Received message: {message_data}")
                        event_orchestrator = EventOrchestrator(redis_client)
                        await event_orchestrator.process(message_data)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
            await asyncio.sleep(0.01)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Redis client...")
    r = redis.Redis(host=config.redis_host, port=config.redis_port, db=config.redis_db)
    app.state.redis_client = r

    # Start listener
    task = asyncio.create_task(redis_listener(r))
    yield

    # Cleanup
    task.cancel()
    # await r.aclose()
    logger.info("Redis client closed.")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="Orchestrator Service")
    return app


app = create_app()


@app.get("/")
async def root():
    return {"message": "Orchestrator is running"}
