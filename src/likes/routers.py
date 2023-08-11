from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.likes.crud import add_like
from src.likes.schemas import UserLikeRequest, UserLikeResponse

likes_router = APIRouter(
    prefix="/likes",
    tags=["Like"],
)


# TODO: add dependency to get UserLike from token + body when jwt is ready
@likes_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserLikeResponse,
)
async def like_user(
    user_like: UserLikeRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    like = await add_like(user_like, session)

    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="bad user id",
        )

    return UserLikeResponse.from_orm(like)
