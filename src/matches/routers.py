from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.exceptions import NotFoundException, PermissionDeniedException
# TODO логика из likes?
from src.likes.crud import get_like_by_user_ids, perform_destroy_like
from src.matches.crud import get_match_by_match_id, delete_match, get_questionnaires_by_user_matched
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
async def match_delete(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
    match_id: UUID,
):
    # TODO выносим в crud / или переорганизуем логику -> сделаем атомарной
    match = await get_match_by_match_id(session, match_id)
    if not match:
        raise NotFoundException(f"Match with id={match_id} doesn't found")

    if user.id not in (match.user1_id, match.user2_id):
        raise PermissionDeniedException

    another_user_id = match.user1_id if user.id == match.user2_id else match.user2_id
    like = await get_like_by_user_ids(
        session,
        user_id=user.id,
        liked_user_id=another_user_id,
    )

    if not like:
        raise NotFoundException(
            f"Like from user {user.id} to user {another_user_id} not found",
        )

    await delete_match(session, match)
    await perform_destroy_like(session, like)
