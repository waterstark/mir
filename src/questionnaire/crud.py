from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.questionnaire.models import UserQuestionnaire, UserQuestionnaireHobby
from src.questionnaire.schemas import (
    CreateUserQuestionnaireSchema,
    ResponseUserQuestionnaireSchema,
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
    user_profile_dict = {**user_profile.dict(exclude={"hobbies"})}
    questionnaire = UserQuestionnaire(**user_profile_dict)
    hobbies = user_profile.hobbies
    for hobby in hobbies:
        hobby_obj = UserQuestionnaireHobby(hobby_name=hobby.hobby_name)
        questionnaire.hobbies.append(hobby_obj)
    session.add(questionnaire)
    await session.commit()
    return ResponseUserQuestionnaireSchema(**questionnaire.__dict__)


async def update_questionnaire(
    quest_id: UUID,
    update_value: CreateUserQuestionnaireSchema,
    session: AsyncSession,
):
    update_value_dict = update_value.dict(exclude={"hobbies", "user_id"})
    stmt = select(UserQuestionnaire).where(UserQuestionnaire.id == quest_id)
    result = await session.execute(stmt)
    questionnaire = result.scalar_one_or_none()
    stmt = (
        update(UserQuestionnaire)
        .values(update_value_dict)
        .where(UserQuestionnaire.id == quest_id)
        .returning(UserQuestionnaire)
    )
    await session.execute(stmt)
    questionnaire.hobbies = []
    for hobby in update_value.hobbies:
        hobby_item = UserQuestionnaireHobby(hobby_name=hobby.hobby_name)
        questionnaire.hobbies.append(hobby_item)
    await session.commit()
    return ResponseUserQuestionnaireSchema(**questionnaire.__dict__)


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
        query_questionnaire = delete(UserQuestionnaire).where(
            UserQuestionnaire.id == quest_id,
        )
        await session.execute(query_questionnaire)
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
