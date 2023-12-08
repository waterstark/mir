import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.likes.crud import get_like_by_user_ids
from src.matches.crud import create_match


async def create_match_after_like(
    session: AsyncSession,
    user1_id: UUID,
    user2_id: UUID,
):
    likes = await asyncio.gather(
        get_like_by_user_ids(session, user1_id, user2_id),
        get_like_by_user_ids(session, user2_id, user1_id),
    )

    if likes[0] is not None and likes[1] is not None \
            and likes[0].is_liked and likes[1].is_liked:
        await asyncio.create_task(
            create_match(session, user1_id, user2_id),
        )
