import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from async_asgi_testclient import TestClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.mongodb.mongodb import Mongo
from src.redis.redis import redis as redis_client

if settings.TEST_DB_NAME:
    settings.DB_NAME = settings.TEST_DB_NAME

engine = create_async_engine(settings.test_db_url_postgresql, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

pytest_plugins = [
    "tests.fixtures",
]


@pytest.fixture(autouse=True, scope="module")
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    from src.database import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await redis_client.flush_db()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[TestClient, None]:
    from src.main import app

    async with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def mongo() -> AsyncGenerator[Mongo, None]:
    from src.database import mongo
    return mongo
