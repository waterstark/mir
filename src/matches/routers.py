from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.exceptions import NotFoundException, PermissionDeniedException
from src.likes.crud import get_retreive_like, perform_destroy_like
from src.likes.schemas import UserLikeRequest
from src.matches.crud import get_match_by_id, perform_destroy_match
from src.matches.models import Match
from src.questionnaire.models import UserQuestionnaire
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
    stmt = (
        select(AuthUser, UserQuestionnaire)
        .join(
            Match,
            or_(
                and_(Match.user1_id == user.id, Match.user2_id == AuthUser.id),
                and_(Match.user2_id == user.id, Match.user1_id == AuthUser.id),
            ),
        )
        .join(UserQuestionnaire, UserQuestionnaire.user_id == AuthUser.id)
    )

    result = (await session.execute(stmt)).fetchall()

    # TODO: Придумать что-то логичное вместо этого костыля :)
    for _, questionnaire in result:
        questionnaire.is_match = True

    return [questionnaire for _, questionnaire in result]


@router.delete(
    path="/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def match_delete(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
    match_id: UUID,
):
    match = await get_match_by_id(session, match_id)
    if not match:
        raise NotFoundException(f"Match with id={match_id} doesn't found")

    if user.id not in (match.user1_id, match.user2_id):
        raise PermissionDeniedException

    another_user_id = match.user1_id if user.id == match.user2_id else match.user2_id
    like = await get_retreive_like(
        session,
        UserLikeRequest(user_id=user.id, liked_user_id=another_user_id),
    )

    if not like:
        raise NotFoundException(
            f"Like from user {user.id} to user {another_user_id} not found",
        )

    await perform_destroy_match(session, match)
    await perform_destroy_like(session, like)
