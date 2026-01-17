from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.settings import settings

from app.auth.router import router as auth_router
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    app.state.redis = Redis.from_url(
        url=settings.REDIS_URL, encoding="utf-8", decode_responses=True
    )

    yield

    await app.state.redis.close()
    print("Shutting down...")


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
