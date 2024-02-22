from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.exceptions import AlreadyExistsException, NotFoundException, PermissionDeniedException, SelfMatchException
from src.likes.crud import delete_like, get_like_by_user_ids
from src.matches.models import Match
from src.questionnaire.models import UserQuestionnaire


async def get_match_by_user_ids(
    session: AsyncSession,
    user1_id: UUID,
    user2_id: UUID,
) -> Match | None:
    """Getting a Match between user 1 and user 2 by their ID."""
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


async def get_questionnaires_by_user_matched(
    session: AsyncSession,
    user: AuthUser,
) -> list[UserQuestionnaire]:
    """Getting all the questionnaires for which the Match occurred."""
    query = (
        select(Match, UserQuestionnaire)
        .join(
            Match,
            or_(
                and_(Match.user1_id == user.id, Match.user2_id == UserQuestionnaire.user_id),
                and_(Match.user2_id == user.id, Match.user1_id == UserQuestionnaire.user_id),
            ),
        )
    )
    result = (await session.execute(query)).fetchall()

    await change_questionnaire_match_info(result)

    return [questionnaire for _, questionnaire in result]


async def change_questionnaire_match_info(query_result: Sequence[tuple[Match, UserQuestionnaire]]) -> None:
    # TODO: Придумать что-то логичное вместо этого костыля, возможно перенести логику в likes
    """The function changes the value of is_match in the Questionnaire model to True."""
    for match, questionnaire in query_result:
        questionnaire.is_match = True
        questionnaire.match_id = match.id


async def get_match_by_match_id(
    session: AsyncSession,
    match_id: UUID,
) -> Match | None:
    """Getting a Match by its Match_ID."""
    return await session.get(Match, match_id)


async def get_matches_by_user(
    session: AsyncSession,
    user: AuthUser,
) -> Sequence[Match]:
    """Getting a list of all the user's Matches."""
    stmt = select(Match).where(
        or_(Match.user1_id == user.id, Match.user2_id == user.id),
    )
    return (await session.execute(stmt)).scalars().all()


async def create_match(
    session: AsyncSession,
    user1_id: UUID,
    user2_id: UUID,
) -> Match:
    """Creating a Match."""
    await check_match_data(session, user1_id, user2_id)
    stmt = insert(Match).values({
        Match.user1_id: user1_id,
        Match.user2_id: user2_id,
    }).returning(Match)

    match = (await session.execute(stmt)).scalar_one_or_none()
    await session.commit()
    return match


async def check_match_data(
    session: AsyncSession,
    user1_id: UUID,
    user2_id: UUID,
) -> None:
    """Checking for the lack of a Match with himself and for duplicate Matches."""
    if user1_id == user2_id:
        raise SelfMatchException

    query = select(Match).where(
            or_(
                and_(Match.user1_id == user1_id, Match.user2_id == user2_id),
                and_(Match.user2_id == user1_id, Match.user1_id == user2_id),
            ))
    matches = (await session.execute(query)).all()

    if matches:
        raise AlreadyExistsException


async def remove_match(
    session: AsyncSession,
    user: AuthUser,
    match_id: UUID,
) -> None:
    """Deleting a Match from the database."""
    match = await get_match_by_match_id(session, match_id)
    if not match:
        raise NotFoundException(f"Match with id={match_id} doesn't found")

    if user.id not in (match.user1_id, match.user2_id):
        raise PermissionDeniedException

    liked_user_id = match.user1_id if user.id == match.user2_id else match.user2_id
    like = await get_like_by_user_ids(
        session,
        user_id=user.id,
        liked_user_id=liked_user_id,
    )

    await delete_match(session, match)
    await delete_like(session, like)


async def delete_match(
    session: AsyncSession,
    match: Match,
) -> None:
    await session.delete(match)
    await session.commit()
