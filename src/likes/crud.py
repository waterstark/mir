from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import AlreadyExistsException, SelfLikeException
from src.likes.models import UserLike
from src.likes.schemas import UserLikeRequest


async def add_like(user_like: UserLikeRequest, session: AsyncSession):
    stmt = (
        insert(UserLike)
        .values(
            {
                UserLike.user_id: user_like.user_id,
                UserLike.liked_user_id: user_like.liked_user_id,
                UserLike.is_liked: user_like.is_liked,
            },
        )
        .returning(UserLike)
    )

    try:
        like = (await session.execute(stmt)).scalar_one_or_none()
        await session.commit()
        return like
    except SQLAlchemyError:
        return None


async def get_all_likes(session: AsyncSession) -> list[UserLike]:
    return (await session.execute(select(UserLike))).scalars().all()


async def get_retreive_like(
    session: AsyncSession,
    like_data: UserLikeRequest,
) -> UserLike | None:
    stmt = select(UserLike).where(
        UserLike.liked_user_id == like_data.liked_user_id,
        UserLike.user_id == like_data.user_id,
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_like_by_id(session: AsyncSession, like_id: UUID) -> UserLike | None:
    return await session.get(UserLike, like_id)


async def create_like(
    session: AsyncSession,
    like_data: UserLikeRequest,
) -> UserLike | None:
    await check_like_data(session, like_data)
    stmt = insert(UserLike).values(like_data.dict()).returning(UserLike)

    like = (await session.execute(stmt)).scalar_one_or_none()
    await session.commit()
    return like


async def check_like_data(session: AsyncSession, like_data: UserLikeRequest):
    if like_data.liked_user_id == like_data.user_id:
        raise SelfLikeException

    likes = await get_all_likes(session)
    if [
        like
        for like in likes
        if like.user_id == like_data.user_id
        and like.liked_user_id == like_data.liked_user_id
    ]:
        raise AlreadyExistsException


async def perform_destroy_like(session: AsyncSession, like: UserLike):
    await session.delete(like)
    await session.commit()
