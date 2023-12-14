from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.matches.crud import get_questionnaires_by_user_matched, delete_match_from_database
from src.questionnaire.schemas import (
    ResponseQuestionnaireSchemaWithMatch,
)

router = APIRouter(
    prefix="/matches",
    tags=["Match"],
)


@router.get(
    path="",
    response_model=list[ResponseQuestionnaireSchemaWithMatch],
)
async def get_matches(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
):
    return await get_questionnaires_by_user_matched(session=session, user=user)


@router.delete(
    path="/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_match(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
    match_id: UUID,
):
    return await delete_match_from_database(session=session, user=user, match_id=match_id)
