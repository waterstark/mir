from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.matches.models import Match
from src.matches.schemas import MatchRequest


async def get_match_list(session: AsyncSession, id: UUID | None = None):
    stmt = select(Match)
    if id:
        stmt = select(Match).filter(or_(Match.user1_id == id, Match.user1_id == id))
    matches = await session.execute(stmt)
    return matches.scalars().all()


async def get_retrieve_match(session: AsyncSession, match_id: int):
    stmt = select(Match).where(Match.id == match_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def perform_destroy_match(session: AsyncSession, match: MatchRequest):
    await session.delete(match)
    await session.commit()


async def perform_create_match(session: AsyncSession, data: MatchRequest):
    session.add(Match(**data.dict()))
    await session.commit()
