from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.questionnaire import crud
from src.questionnaire.schemas import (
    CreateUserQuestionnaireSchema,
    ResponseUserQuestionnaireSchema,
)

router = APIRouter(
    prefix="/questionnaire",
    tags=["Questionnaire"],
)


@router.post(
    "",
    response_model=ResponseUserQuestionnaireSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_questionnaire(
    user_profile: CreateUserQuestionnaireSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
):
    return await crud.create_questionnaire(user_profile, session, user)


@router.get(
    "/list/{page_number}",
    response_model=list[ResponseUserQuestionnaireSchema],
    status_code=status.HTTP_200_OK,
)
async def get_list_questionnaire(
    user: Annotated[AuthUser, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    page_number: Annotated[int, Path(ge=0)],
):
    return await crud.get_list_questionnaire(user, session, page_number)


@router.get(
    "/get_my_quest",
    response_model=ResponseUserQuestionnaireSchema,
    status_code=status.HTTP_200_OK,
)
async def get_questionnaire(
    user: Annotated[AuthUser, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await crud.get_questionnaire(user.id, session)


@router.patch(
    "/{quest_id}",
    response_model=ResponseUserQuestionnaireSchema,
    status_code=status.HTTP_200_OK,
)
async def update_quest(
    quest_id: UUID,
    update_value: CreateUserQuestionnaireSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
):
    return await crud.update_questionnaire(quest_id, update_value, session, user)


@router.delete(
    "/{quest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quest(
    user: Annotated[AuthUser, Depends(current_user)],
    quest_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await crud.delete_quest(user, quest_id, session)
