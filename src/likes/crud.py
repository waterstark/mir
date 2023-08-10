from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.likes.models import UserLike
from src.likes.schemas import UserLikeRequest


async def add_like(session: AsyncSession, **data: dict):
    stmt = insert(UserLike).values(data).returning(UserLike)
    try:
        like = (await session.execute(stmt)).scalar_one_or_none()
        await session.commit()
    except SQLAlchemyError as e:
        return str(e.orig).split(": ")[2]
    return like


async def get_retreive_like(session: AsyncSession, user_like: UserLikeRequest):
    stmt = select(UserLike).where(
        UserLike.liked_user_id == user_like.liked_user_id,
        UserLike.user_id == user_like.user_id,
    )
    return (await session.execute(stmt)).scalar_one_or_none()
