from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, select, update, desc
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.database import async_session_maker
from src.likes.models import UserLike
from src.questionnaire.models import UserQuestionnaire, UserQuestionnaireHobby
from src.questionnaire.schemas import (
    CreateUserQuestionnaireSchema,
    ResponseUserQuestionnaireSchema,
)


async def get_list_questionnaire(
    user: AuthUser,
    session: AsyncSession,
    page_number: int,
):
    user_questionnaire = await get_questionnaire(user_id=user.id, session=session)
    if user_questionnaire.quest_lists_per_day >= 3:
        return []

    user_questionnaire.quest_lists_per_day += 1
    await session.commit()

    is_visible = True
    liked_user_ids = (
        select(UserLike.liked_user_id)
        .where(UserLike.user_id == user.id)
    )
    query_1 = (
        select(UserQuestionnaire)
        .where(
            UserQuestionnaire.user_id != user.id,
            UserQuestionnaire.city == user_questionnaire.city,
            UserQuestionnaire.gender != user_questionnaire.gender,
            UserQuestionnaire.is_visible == is_visible,
            UserQuestionnaire.user_id.notin_(liked_user_ids),
            UserQuestionnaire.rate >= user_questionnaire.rate
        )
        .order_by(UserQuestionnaire.rate)
        .limit(3).offset(page_number)
    )
    query_2 = (
        select(UserQuestionnaire)
        .where(
            UserQuestionnaire.user_id != user.id,
            UserQuestionnaire.city == user_questionnaire.city,
            UserQuestionnaire.gender != user_questionnaire.gender,
            UserQuestionnaire.is_visible == is_visible,
            UserQuestionnaire.user_id.notin_(liked_user_ids),
            UserQuestionnaire.rate < user_questionnaire.rate
        )
        .order_by(desc(UserQuestionnaire.rate))
        .limit(3).offset(page_number)
    )
    result_1 = await session.execute(query_1)
    result_2 = await session.execute(query_2)
    query_1_results = result_1.scalars().fetchall()
    query_2_results = result_2.scalars().fetchall()
    combined_results = query_1_results + query_2_results

    return combined_results


async def create_questionnaire(
    user_profile: CreateUserQuestionnaireSchema,
    session: AsyncSession,
    user: AuthUser,
):
    select_user_questionnaire = await get_questionnaire(
        user_id=user.id,
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
    questionnaire = UserQuestionnaire(user_id=user.id, **user_profile_dict)
    today = date.today()
    min_age = today.replace(year=today.year - 18)
    max_age = today.replace(year=today.year - 82)
    if questionnaire.birthday > min_age and questionnaire.birthday < max_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Возрастное ограничение строго c 18 лет!",
        )
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
    user: AuthUser,
):
    update_value_dict = update_value.dict(exclude={"hobbies", "user_id"})
    stmt = select(UserQuestionnaire).where(
        and_(UserQuestionnaire.id == quest_id,
             UserQuestionnaire.user_id == user.id),
    )
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


async def reset_quest_lists_per_day():
    try:
        async with async_session_maker() as session:
            stmt = (
                update(UserQuestionnaire)
                .values(quest_lists_per_day=0)
            )
            await session.execute(stmt)
            await session.commit()
    except ProgrammingError:
        pass
