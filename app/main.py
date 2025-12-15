from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.config import get_settings
from app.routers import health_router, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )
    app.state.redis = redis_client
    try:
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(title="Phone-Address Service", lifespan=lifespan)
app.include_router(router)
app.include_router(health_router)
