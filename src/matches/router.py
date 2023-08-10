from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.database import get_async_session
from src.matches.crud import get_match_list, get_retrieve_match, perform_destroy_match
from src.matches.schemas import MatchResponse

router = APIRouter(
    prefix="/matches",
    tags=["Match"],
)


@router.get(
    path="",
    response_model=list[MatchResponse],
)
async def get_matches(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
):
    return await get_match_list(session, id=user.id)


@router.delete(
    path="/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def match_delete(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[AuthUser, Depends(current_user)],
    match_id: int,
):
    match = await get_retrieve_match(session, match_id)

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match doesn't exists",
        )

    if user.id not in (match.user1_id, match.user2_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't access to delete this match",
        )

    await perform_destroy_match(session, match)
