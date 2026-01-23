from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.settings import settings

from app.auth.router import router as auth_router
from app.users.router import router as users_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")

    try:
        app.state.redis = Redis.from_url(
            url=settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        await app.state.redis.ping()  # type: ignore
        logger.info("Redis connection established successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise e

    yield

    if hasattr(app.state, "redis"):
        await app.state.redis.close()
        logger.info("Redis connection closed.")

    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
)


app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])


@app.get("/")
async def root():
    return {"status": "ok", "docs": f"{settings.API_PREFIX}/docs"}
