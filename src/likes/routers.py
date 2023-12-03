from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.likes.crud import add_like
from src.likes.schemas import UserLikeRequest, UserLikeResponse
from src.matches.utils import create_match_after_like

likes_router = APIRouter(
    prefix="/likes",
    tags=["Like"],
)


@likes_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserLikeResponse,
)
async def like_user(
    user: Annotated[AuthUser, Depends(current_user)],
    user_like: UserLikeRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    bg_tasks: BackgroundTasks,
):
    like = await add_like(user, user_like, session)

    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="bad user id",
        )

    bg_tasks.add_task(create_match_after_like, session, user.id, user_like.liked_user_id)

    return UserLikeResponse.from_orm(like)
