from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import status
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database import get_async_session
from src.questionary.models import UserQuestionnaire
from src.questionary.schemas import UserQuestionaryResponse, UserQuestionnaireSchema

router = APIRouter(
    prefix="/quest",
    tags=["questionary"],
)


@router.post("/questionary", response_model=UserQuestionaryResponse, status_code=status.HTTP_201_CREATED)
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
