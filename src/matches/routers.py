from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.exceptions import NotFoundException, PermissionDeniedException
from src.likes.crud import get_retreive_like, perform_destroy_like
from src.likes.schemas import UserLikeRequest
from src.matches.crud import get_match_by_id, get_user_matches, perform_destroy_match
from src.questionnaire.crud import get_questionnaire_by_user_id
from src.questionnaire.schemas import UserQuestionnaireResponse

router = APIRouter(
    prefix="/matches",
    tags=["Match"],
)

# TODO: Подумать, как через join
# оптимизировать забор связанных анкет из таблицы
@router.get(
    path="",
    response_model=list[UserQuestionnaireResponse],
)
async def get_matches(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
):
    matches = await get_user_matches(session, user)
    response = []
    for match in matches:
        another_user_id = (
            match.user1_id if user.id == match.user2_id else match.user2_id
        )
        questionnaire = await get_questionnaire_by_user_id(session, another_user_id)
        questionnaire = UserQuestionnaireResponse.from_orm(questionnaire)
        questionnaire.is_match = True
        response.append(questionnaire)
    return response


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
