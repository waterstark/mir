from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings
from src.mongodb.mongodb import Mongo


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.db_url_postgresql, echo=False)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_async_session_as_session() -> AsyncSession:
    async with async_session_maker() as session:
        return session

mongo = Mongo()
