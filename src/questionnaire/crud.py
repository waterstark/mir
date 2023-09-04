from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.questionnaire.models import UserQuestionnaire


async def get_questionnaire_by_user_id(
    session: AsyncSession,
    user_id: UUID,
) -> list[UserQuestionnaire]:
    stmt = select(UserQuestionnaire).where(user_id == user_id)
    return (await session.execute(stmt)).scalar_one_or_none()
