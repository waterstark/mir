from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.questionnaire.models import UserQuestionnaire
from src.questionnaire.schemas import (
    CreateUserQuestionnaireSchema,
)


async def get_list_questionnaire_first_10(
    user: AuthUser,
    session: AsyncSession,
):
    user_questionnaire = await get_questionnaire(user_id=user.id, session=session)
    is_visible = True
    query = (
        select(UserQuestionnaire)
        .where(
            UserQuestionnaire.user_id != user.id,
            UserQuestionnaire.city == user_questionnaire.city,
            UserQuestionnaire.gender != user_questionnaire.gender,
            UserQuestionnaire.is_visible == is_visible,
        )
        .limit(10)
    )
    result = await session.execute(query)
    return result.scalars().fetchall()


async def create_questionnaire(
    user_profile: CreateUserQuestionnaireSchema,
    session: AsyncSession,
):
    select_user_questionnaire = await get_questionnaire(
        user_id=user_profile.user_id,
        session=session,
    )
    if select_user_questionnaire:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Объект уже существует в базе данных!!!{}".format(
                select_user_questionnaire.firstname,
            ),
        )
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
    update_value: CreateUserQuestionnaireSchema,
    session: AsyncSession,
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
    user: AuthUser,
    quest_id: UUID,
    session: AsyncSession,
):
    user_questionnaire = await get_questionnaire(user_id=user.id, session=session)
    if not user_questionnaire:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой анкеты не существует",
        )
    if user_questionnaire.id == quest_id:
        query = delete(UserQuestionnaire).where(UserQuestionnaire.id == quest_id)
        await session.execute(query)
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Нет доступа к данной анкете!!! {quest_id}",
        )


async def get_questionnaire(user_id: UUID, session: AsyncSession):
    query = select(UserQuestionnaire).where(UserQuestionnaire.user_id == user_id)
    get_user = await session.execute(query)
    response = get_user.scalar()
    if response:
        return response
    return None
