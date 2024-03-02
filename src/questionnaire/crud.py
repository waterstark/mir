from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, select, update, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.database import async_session_maker
from src.likes.models import UserLike
from src.questionnaire.models import UserQuestionnaire, UserQuestionnaireHobby, UsersJointRate
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
    users_joint_rate = (
        select(UsersJointRate)
        .where(or_(UsersJointRate.user_id_1 == user.id, UsersJointRate.user_id_2 == user.id),
               UsersJointRate.user_id_1.notin_(liked_user_ids),
               UsersJointRate.user_id_2.notin_(liked_user_ids),
               )
        .order_by(UsersJointRate.joint_rate)
        .limit(5).offset(page_number)
    )

    query = (
        select(UserQuestionnaire)
        .where(
            UserQuestionnaire.user_id != user.id,
            UserQuestionnaire.user_id.in_(users_joint_rate),
        )
        .limit(5).offset(page_number)
    )
    result = await session.execute(query)
    return result.scalars().fetchall()


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
    await create_users_joint_rate(user_id_1=user.id, session=session)
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


async def create_users_joint_rate(user_id_1: UUID, session: AsyncSession):
    user_questionnaire_1 = await get_questionnaire(user_id=user_id_1, session=session)
    users_questionnaires_query = (
        select(UserQuestionnaire)
        .where(UserQuestionnaire.user_id != user_id_1,
               user_questionnaire_1.gender != UserQuestionnaire.gender,
               UserQuestionnaire.city == user_questionnaire_1.city
               )
    )
    users_questionnaires = await session.execute(users_questionnaires_query)
    users_questionnaires_mas = users_questionnaires.scalars().fetchall()
    for quest in users_questionnaires_mas:
        user_id_2 = quest.user_id
        joint_rate = await joint_rate_calculate(user_id_1, user_id_2, session=session)
        stmt = insert(UsersJointRate).values({
            UsersJointRate.user_id_1: user_id_1,
            UsersJointRate.user_id_2: user_id_2,
            UsersJointRate.joint_rate: joint_rate,
        }).returning(UsersJointRate)
        usersjointrate = (await session.execute(stmt)).scalar_one_or_none()
        await session.commit()

async def joint_rate_calculate(user_id_1: UUID, user_id_2: UUID, session: AsyncSession):
    smoking = {
        "Курю": 1,
        "Нормально": 2,
        "Негативно": 3
    }
    alcohol = {
        "Пью часто": 1,
        "Иногда выпиваю": 2,
        "He пью": 3,
        "Негативно": 4
    }
    sport = {
        "Часто занимаюсь": 1,
        "Иногда занимаюсь": 2,
        "He занимаюсь": 3,
        "He люблю спорт": 4
    }
    joint_rate = 100
    user_questionnaire_1 = await get_questionnaire(user_id=user_id_1, session=session)
    user_questionnaire_2 = await get_questionnaire(user_id=user_id_2, session=session)
    if user_questionnaire_1.smoking and user_questionnaire_2.smoking:
        smoking_num_1 = smoking[user_questionnaire_1.smoking]
        smoking_num_2 = smoking[user_questionnaire_2.smoking]
        joint_rate -= 10 * abs(smoking_num_1 - smoking_num_2)
    if user_questionnaire_1.alcohol and user_questionnaire_2.alcohol:
        alcohol_num_1 = alcohol[user_questionnaire_1.alcohol]
        alcohol_num_2 = alcohol[user_questionnaire_2.alcohol]
        joint_rate -= 10 * abs(alcohol_num_1 - alcohol_num_2)
    if user_questionnaire_1.sport and user_questionnaire_2.sport:
        sport_num_1 = sport[user_questionnaire_1.sport]
        sport_num_2 = sport[user_questionnaire_2.sport]
        joint_rate -= 10 * abs(sport_num_1 - sport_num_2)
    return joint_rate