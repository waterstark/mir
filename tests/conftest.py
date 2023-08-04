import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.config import DATABASE_URL
from src.database import Base, async_session_maker
from src.main import app
||||||| 0257381
from src.database import get_async_session
=======
from src.config import DATABASE_URL
from src.database import Base, async_session_maker, get_async_session
from src.main import app

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)

pytest_plugins = [
    "tests.fixtures",
]


@pytest.fixture()
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
async def _prepare_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
>>>>>>> refs/remotes/origin/main


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def session() -> AsyncGenerator[AsyncSession, None]:
    f = get_async_session()
    session = await f.asend(None)
    yield session
    with contextlib.suppress(StopAsyncIteration):
        await f.asend(None)


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=app, base_url="http://localhost:8000") as client:
        yield client
