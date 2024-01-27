import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import schemas
from src.auth import utils as auth_utils
from src.auth.models import AuthUser, UserSettings
from src.auth.schemas import UserCreateInput, UserSchema


async def get_user(
    email: str,
    session: AsyncSession,
) -> UserSchema:
    """Получение данных o пользователе из БД по email."""
    query = select(AuthUser).where(AuthUser.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_user(
    user_data: UserCreateInput,
    session: AsyncSession,
) -> UserSchema:
    """Создание пользователя в БД."""
    if await get_user(user_data.email, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="register user already exists",
        )
    valid_user_data = UserSchema(
        id=uuid.uuid4(),
        email=user_data.email,
        hashed_password=auth_utils.hash_password(user_data.password),
    )
    stmt = insert(AuthUser).values(**valid_user_data.dict())
    await session.execute(stmt)
    await session.commit()
    await create_user_profile(user=valid_user_data, session=session)
    return valid_user_data


async def add_user(user: UserCreateInput, session: AsyncSession):
    stmt = (
        insert(AuthUser)
        .values(
            {
                AuthUser.email: user.email,
                AuthUser.hashed_password: user.password,
            },
        )
        .returning(AuthUser)
    )

    user = (await session.execute(stmt)).scalar_one_or_none()
    await session.commit()
    return user


async def get_user_profile(
    user: AuthUser,
    session: AsyncSession,
) -> schemas.UserProfile:
    """Get user profile."""
    stmt = select(UserSettings).filter_by(user_id=user.id)
    profile = await session.execute(stmt)
    return schemas.UserProfile.validate(profile.scalars().first())


async def update_user_profile(
    data: schemas.UserProfileUpdate,
    user: AuthUser,
    session: AsyncSession,
) -> schemas.UserProfile:
    """Update user profile."""
    stmt = (
        update(UserSettings)
        .filter_by(user_id=user.id)
        .values(data.dict())
        .returning(UserSettings)
    )
    profile = await session.execute(stmt)
    await session.commit()
    return schemas.UserProfile.validate(profile.scalars().first())


async def create_user_profile(user: AuthUser, session: AsyncSession):
    """Create user profile."""
    stmt = insert(UserSettings).values(
        {
            UserSettings.user_id: user.id,
        },
    )
    await session.execute(stmt)
    await session.commit()
