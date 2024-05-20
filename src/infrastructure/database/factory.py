from typing import AsyncGenerator

from src.infrastructure.database.config import db_config

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker, AsyncSession)


engine = create_async_engine(
    url=db_config.uri,
    echo=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session