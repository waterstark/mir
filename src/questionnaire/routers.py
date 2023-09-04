from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.questionnaire import crud
from src.questionnaire.schemas import UserQuestionnaireResponse, UserQuestionnaireSchema

router = APIRouter(
    prefix="/questionnaire",
    tags=["Questionnaire"],
)


@router.post(
    "",
    response_model=UserQuestionnaireResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_questionnaire(
        user_profile: UserQuestionnaireSchema,
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await crud.create_questionnaire(user_profile, session)


@router.get(
    "/10",
    response_model=list[UserQuestionnaireResponse],
    status_code=status.HTTP_200_OK,
)
async def get_list_questionnaire(
        user: Annotated[AuthUser, Depends(current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await crud.get_list_questionnaire_first_10(user, session)


@router.patch(
    "/{quest_id}",
    response_model=UserQuestionnaireResponse,
    status_code=status.HTTP_200_OK,
)
async def update_quest(
        quest_id: UUID,
        update_value: UserQuestionnaireSchema,
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await crud.update_questionnaire(quest_id, update_value, session)


@router.delete(
    "/{quest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quest(
        quest_id: UUID,
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await crud.delete_quest(quest_id, session)
