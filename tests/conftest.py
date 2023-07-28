import asyncio
from asyncio import AbstractEventLoop
from typing import Generator, Any, AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session


@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# TODO: replace with async context manager
@pytest.fixture(scope='function')
async def session() -> AsyncGenerator[AsyncSession, None]:
    f = get_async_session()
    session = await f.asend(None)
    yield session
    try:
        await f.asend(None)
    except StopAsyncIteration:
        pass
