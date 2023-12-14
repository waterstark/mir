from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.exceptions import AlreadyExistsException, SelfMatchException
from src.matches.models import Match
from src.questionnaire.models import UserQuestionnaire


async def get_match_by_user_ids(
        session: AsyncSession,
        user1_id: UUID,
        user2_id: UUID,
) -> Match | None:
    """Получение Метча между пользователем1 и пользователем2 по их ID."""
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
        user: AuthUser
) -> list[UserQuestionnaire]:
    """Получение всех анкет, по которым произошел Метч."""
    query = (
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
    result = (await session.execute(query)).fetchall()

    await _change_questionnaire_match_info(result)

    return [questionnaire for _, questionnaire in result]


async def _change_questionnaire_match_info(query_result) -> None:
    # TODO: Придумать что-то логичное вместо этого костыля, возможно перенести логику в likes
    """Функция меняет значение is_match в модели Questionnaire на True"""
    for _, questionnaire in query_result:
        questionnaire.is_match = True


async def get_match_by_match_id(
        session: AsyncSession,
        match_id: UUID
) -> Match | None:
    """Получение Метча по его Match_ID."""
    return await session.get(Match, match_id)


async def get_matches_by_user(
        session: AsyncSession,
        user: AuthUser
) -> Sequence[Match]:
    """Получение списка всех Метчей пользователя."""
    stmt = select(Match).where(
        or_(Match.user1_id == user.id, Match.user2_id == user.id),
    )
    return (await session.execute(stmt)).scalars().all()


async def get_all_matches(
        session: AsyncSession
) -> Sequence[Match]:
    """Получение всех Метчей из базы данных."""
    return (await session.execute(select(Match))).scalars().all()


async def create_match(
        session: AsyncSession,
        user1_id: UUID,
        user2_id: UUID
) -> Match:
    """Создание Метча и занесение его в базу данных Match."""
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
        user2_id: UUID
) -> None:
    """
    Проверка на отсутствие Метча с самим собой
    и на дублирование Метчей.
    """
    if user1_id == user2_id:
        raise SelfMatchException

    matches = await get_all_matches(session)
    for match in matches:
        if match.user1_id == user1_id and match.user2_id == user2_id \
                or match.user1_id == user2_id and match.user2_id == user1_id:
            raise AlreadyExistsException


async def delete_match(
        session: AsyncSession,
        match: Match
) -> None:
    """Удаление Метча."""
    await session.delete(match)
    await session.commit()
