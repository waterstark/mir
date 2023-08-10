from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud, schemas
from src.auth.base_config import auth_backend, current_user, fastapi_users_auth
from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput, UserCreateOutput
from src.database import get_async_session

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
