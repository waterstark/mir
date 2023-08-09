from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.likes.models import UserLike
from src.likes.schemas import UserLikeRequest


async def add_like(user_like: UserLikeRequest, session: AsyncSession):
    stmt = (
        insert(UserLike)
        .values(
            {
                UserLike.user_id: user_like.user_id,
                UserLike.liked_user_id: user_like.liked_user_id,
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
