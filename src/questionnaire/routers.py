from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.questionnaire.models import UserQuestionnaire
from src.questionnaire.schemas import UserQuestionnaireResponse, UserQuestionnaireSchema

router = APIRouter(
    prefix="/quest",
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
    stmt = (
        insert(UserQuestionnaire)
        .values(**user_profile.dict())
        .returning(UserQuestionnaire)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.get(
    "",
    response_model=list[UserQuestionnaireResponse],
    status_code=status.HTTP_200_OK,
)
async def get_list_questionnaire(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    query = select(UserQuestionnaire).order_by(UserQuestionnaire.city).fetch(10)
    result = await session.execute(query)
    return result.scalars().fetchall()


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
    stmt = (
        update(UserQuestionnaire)
        .values(**update_value.dict())
        .returning(UserQuestionnaire)
        .where(UserQuestionnaire.id == quest_id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.delete(
    "/{quest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quest(
    quest_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    query = delete(UserQuestionnaire).where(UserQuestionnaire.id == quest_id)
    await session.execute(query)
    await session.commit()
