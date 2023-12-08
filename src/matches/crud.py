from uuid import UUID

from sqlalchemy import and_, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.exceptions import AlreadyExistsException, SelfMatchException
from src.matches.models import Match


async def get_all_matches(session: AsyncSession) -> list[Match]:
    return (await session.execute(select(Match))).scalars().all()


async def get_user_matches(session: AsyncSession, user: AuthUser) -> list[Match]:
    stmt = select(Match).filter(
        or_(Match.user1_id == user.id, Match.user2_id == user.id),
    )
    matches = await session.execute(stmt)
    return matches.scalars().all()


async def get_match_by_user_ids(
    session: AsyncSession,
    user1_id: UUID,
    user2_id: UUID,
) -> Match | None:
    stmt = select(Match).where(or_(
        and_(
            Match.user1_id == user1_id,
            Match.user2_id == user2_id,
        ), and_(
            Match.user1_id == user2_id,
            Match.user2_id == user1_id,
        ),
    ))
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


async def create_match(session: AsyncSession, user1_id: UUID, user2_id: UUID) -> Match:
    await check_match_data(session, user1_id, user2_id)
    stmt = insert(Match).values({
        Match.user1_id: user1_id,
        Match.user2_id: user2_id,
    }).returning(Match)

    match = (await session.execute(stmt)).scalar_one_or_none()
    await session.commit()
    return match


async def check_match_data(session: AsyncSession, user1_id: UUID, user2_id: UUID) -> None:
    if user1_id == user2_id:
        raise SelfMatchException

    matches = await get_all_matches(session)
    for match in matches:
        if match.user1_id == user1_id and match.user2_id == user2_id \
                or match.user1_id == user2_id and match.user2_id == user1_id:
            raise AlreadyExistsException
