import asyncio
import contextlib
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
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

