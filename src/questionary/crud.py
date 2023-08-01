from fastapi import APIRouter, status, Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.questionary.models import UserQuestionnaire
from src.database import get_async_session
from src.questionary.schemas import UserQuestionnaireSchema, UserQuestionaryResponse
from typing import Annotated

router = APIRouter()


@router.get("/questionary", response_model=UserQuestionaryResponse, status_code=status.HTTP_201_CREATED)
async def create_questionary(
        user_profile: UserQuestionnaireSchema,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    stmt = (
        insert(UserQuestionnaire)
        .values(**user_profile.dict())
        .returning(UserQuestionnaire)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()
