from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud, schemas
from src.auth.base_config import auth_backend, current_user, fastapi_users_auth
from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput, UserCreateOutput
from src.database import get_async_session
from src.likes.crud import add_like, get_retreive_like
from src.likes.schemas import UserLikeRequest, UserLikeResponse
from src.matches.crud import perform_create_match
from src.matches.schemas import MatchRequest

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

auth_router.include_router(fastapi_users_auth.get_auth_router(auth_backend))
auth_router.include_router(
    fastapi_users_auth.get_register_router(
        UserCreateOutput,
        UserCreateInput,
    ),
)

user_router = APIRouter(
    prefix="/users",
    tags=["Like"],
)


user_router = APIRouter(
    prefix="/users",
    tags=["Auth"],
)


@user_router.get(
    "/me",
    response_model=schemas.UserProfile,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    user: Annotated[AuthUser, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> schemas.UserProfile:
    return await crud.get_user_profile(user=user, session=session)


@user_router.patch(
    "/me",
    response_model=schemas.UserProfile,
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    data: schemas.UserProfileUpdate,
    user: Annotated[AuthUser, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> schemas.UserProfile:
    """Update user profile."""
    return await crud.update_user_profile(
        data=data,
        user=user,
        session=session,
    )


@user_router.post(
    "/{user_id}/like",
    status_code=status.HTTP_201_CREATED,
    response_model=UserLikeResponse,
)
async def like_user(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    cur_user: Annotated[AuthUser, Depends(current_user)],
    user_id: UUID,
):
    res = await add_like(session, user_id=cur_user.id, liked_user_id=user_id)
    if isinstance(res, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res,
        )

    check_like_data = UserLikeRequest(user_id=user_id, liked_user_id=cur_user.id)
    if await get_retreive_like(session, check_like_data):
        match_data = MatchRequest(user1_id=user_id, user2_id=cur_user.id)
        await perform_create_match(session, match_data)
    return UserLikeResponse.from_orm(res)
