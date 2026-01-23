from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.settings import settings
from typing import AsyncGenerator

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

local_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as session:
        yield session
