from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.questionnaire.models import UserQuestionnaire, UserQuestionnaireHobby
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
    user_profile_dict = {**user_profile.dict(exclude={"hobbies"})}
    questionnaire = UserQuestionnaire(**user_profile_dict)
    hobbies = user_profile.hobbies
    for hobby in hobbies:
        hobby_obj = UserQuestionnaireHobby(hobby_name=hobby.hobby_name)
        questionnaire.hobbies.append(hobby_obj)
    session.add(questionnaire)
    await session.commit()
    return UserQuestionnaireResponse(**questionnaire.__dict__)


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
    update_value_dict = update_value.dict(exclude={"hobbies"})
    stmt = select(UserQuestionnaire).where(UserQuestionnaire.id == quest_id)
    result = await session.execute(stmt)
    questionnaire = result.scalar_one_or_none()
    for key, value in update_value_dict.items():
        setattr(questionnaire, key, value)
    questionnaire.hobbies = []
    for hobby in update_value.hobbies:
        hobby_item = UserQuestionnaireHobby(hobby_name=hobby.hobby_name)
        questionnaire.hobbies.append(hobby_item)
    await session.commit()
    return UserQuestionnaireResponse(**questionnaire.__dict__)


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
