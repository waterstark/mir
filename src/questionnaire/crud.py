from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.questionnaire.models import UserQuestionnaire
from src.questionnaire.schemas import UserQuestionnaireSchema


async def get_list_questionnaire_first_10(
        user: Annotated[AuthUser, Depends(current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    get_user_questionnaire = select(UserQuestionnaire).filter_by(user_id=user.id)
    get_user = await session.execute(get_user_questionnaire)
    user_questionnaire = get_user.fetchone()[0]
    is_visible = True
    query = select(UserQuestionnaire).where(
        UserQuestionnaire.user_id != user.id,
        UserQuestionnaire.city == user_questionnaire.city,
        UserQuestionnaire.gender != user_questionnaire.gender,
        UserQuestionnaire.is_visible == is_visible,
    ).limit(10)
    result = await session.execute(query)
    return result.scalars().fetchall()


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


async def update_questionnaire(
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


async def delete_quest(
        quest_id: UUID,
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    query = delete(UserQuestionnaire).where(UserQuestionnaire.id == quest_id)
    await session.execute(query)
    await session.commit()
