from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.exceptions import AlreadyExistsException, SelfLikeException
from src.likes.models import UserLike
from src.likes.schemas import UserLikeRequest
from src.questionnaire.crud import get_questionnaire


async def add_like(user: AuthUser, user_like: UserLikeRequest, session: AsyncSession):
    stmt = (
        insert(UserLike)
        .values(
            {
                UserLike.user_id: user.id,
                UserLike.liked_user_id: user_like.liked_user_id,
                UserLike.is_liked: user_like.is_liked,
            },
        )
        .returning(UserLike)
    )

    user_questionnaire = await get_questionnaire(user_id=user_like.liked_user_id, session=session)
    if not user_questionnaire:
        raise HTTPException(status_code=404, detail="questionanire not found")

    if user_like.is_liked:
        plus_rate = 50 * (1000/user_questionnaire.rate)
        if plus_rate > 150:
            plus_rate = 150
        user_questionnaire.rate += plus_rate
    elif not user_like.is_liked:
        minus_rate = 10 * (user_questionnaire.rate / 1000)
        if minus_rate > 30:
            minus_rate = 30
        user_questionnaire.rate -= minus_rate

    try:
        like = (await session.execute(stmt)).scalar_one_or_none()
        await session.commit()
        await session.close()
        return like
    except SQLAlchemyError:
        await session.close()
        return None


async def get_all_likes(session: AsyncSession) -> list[UserLike]:
    return (await session.execute(select(UserLike))).scalars().all()


async def get_like_by_user_ids(
    session: AsyncSession,
    user_id: UUID,
    liked_user_id: UUID,
) -> UserLike | None:
    stmt = select(UserLike).where(
        UserLike.liked_user_id == liked_user_id,
        UserLike.user_id == user_id,
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


async def delete_like(session: AsyncSession, like: UserLike):
    await session.delete(like)
    await session.commit()
