import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from async_asgi_testclient import TestClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.config import settings
from src.database import Base, async_session_maker
from src.main import app
from src.mongodb.mongodb import Mongo

engine = create_async_engine(settings.db_url_postgresql, poolclass=NullPool)

pytest_plugins = [
    "tests.fixtures",
]


@pytest.fixture(autouse=True, scope="module")
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[TestClient, None]:
    async with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def mongo() -> AsyncGenerator[Mongo, None]:
    from src.database import mongo
    return mongo
