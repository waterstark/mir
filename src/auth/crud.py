from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput


async def add_user(user: UserCreateInput, session: AsyncSession):
    stmt = insert(AuthUser).values(
        {
            AuthUser.email: user.email,
            AuthUser.hashed_password: user.password,
        },
    ).returning(AuthUser)

    user = (await session.execute(stmt)).scalar_one_or_none()
    await session.commit()
    return user
