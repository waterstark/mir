import contextlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud, schemas
from src.auth.base_config import auth_backend, current_user, fastapi_users_auth
from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput, UserCreateOutput
from src.database import get_async_session
from src.exceptions import NotFoundException
from src.likes.crud import create_like, get_retreive_like
from src.likes.schemas import UserLikeRequest
from src.matches.crud import create_match
from src.matches.schemas import MatchRequest
from src.questionnaire.crud import get_questionnaire
from src.questionnaire.schemas import (
    ResponseQuestionnaireSchemaWithMatch,
)

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
    tags=["User"],
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
    response_model=ResponseQuestionnaireSchemaWithMatch,
)
async def like_user_by_id(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    cur_user: Annotated[AuthUser, Depends(current_user)],
    user_id: UUID,
):
    questionnaire = await get_questionnaire(user_id, session)
    if not questionnaire:
        raise NotFoundException("Questionnaire for liked user not found")
    response = ResponseQuestionnaireSchemaWithMatch.from_orm(questionnaire)

    await create_like(
        session,
        UserLikeRequest(user_id=cur_user.id, liked_user_id=user_id),
    )

    match = None
    if await get_retreive_like(
        session,
        UserLikeRequest(user_id=user_id, liked_user_id=cur_user.id),
    ):
        with contextlib.suppress(HTTPException):
            match = await create_match(
                session,
                MatchRequest(user1_id=cur_user.id, user2_id=user_id),
            )

    if match:
        response.is_match = True

    return response
