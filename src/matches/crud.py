from uuid import UUID

from sqlalchemy import insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.exceptions import AlreadyExistsException, SelfMatchException
from src.matches.models import Match
from src.matches.schemas import MatchRequest


async def get_all_matches(session: AsyncSession) -> list[Match]:
    return (await session.execute(select(Match))).scalars().all()


async def get_user_matches(session: AsyncSession, user: AuthUser) -> list[Match]:
    stmt = select(Match).filter(
        or_(Match.user1_id == user.id, Match.user2_id == user.id),
    )
    matches = await session.execute(stmt)
    return matches.scalars().all()


async def get_retreive_match(
    session: AsyncSession,
    match_data: MatchRequest,
) -> Match | None:
    stmt = select(Match).where(
        Match.user1_id == match_data.user1_id,
        Match.user2_id == match_data.user2_id,
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_match_by_id(session: AsyncSession, match_id: UUID) -> Match | None:
    return await session.get(Match, match_id)


async def get_matches_by_user(session: AsyncSession, user: AuthUser) -> list[Match]:
    stmt = select(Match).where(
        or_(Match.user1_id == user.id, Match.user2_id == user.id),
    )
    return (await session.execute(stmt)).scalars().all()


async def perform_destroy_match(session: AsyncSession, match: Match) -> None:
    await session.delete(match)
    await session.commit()


async def create_match(session: AsyncSession, match_data: MatchRequest) -> Match:
    await check_match_data(session, match_data)
    stmt = insert(Match).values(match_data.dict()).returning(Match)

    match = (await session.execute(stmt)).scalar_one_or_none()
    await session.commit()
    return match


async def check_match_data(session: AsyncSession, match_data: MatchRequest) -> None:
    if match_data.user1_id == match_data.user2_id:
        raise SelfMatchException

    matches = await get_all_matches(session)
    if [
        match
        for match in matches
        if match.user1_id == match.user1_id
        and match.user2_id == match.user2_id
        or match.user1_id == match.user2_id
        and match.user2_id == match.user1_id
    ]:
        raise AlreadyExistsException
