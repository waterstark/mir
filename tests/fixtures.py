import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import get_jwt_strategy
from src.auth.models import AuthUser
from src.likes.models import UserLike
from src.main import app
from src.matches.models import Match
from src.questionnaire.models import UserQuestionnaire

user_data = {
    "email": "test_user@server.com",
    "password": "pass",
}

user2_data = {
    "email": "test_user2@server.com",
    "password": "pass",
}

user3_data = {
    "email": "test_user3@server.com",
    "password": "pass",
}

user_questionary_data = {
    "firstname": "Anton",
    "lastname": "Pupkin",
    "gender": "Male",
    "photo": "False",
    "country": "False",
    "city": "False",
    "about": "False",
    "passion": "Путешествия",
    "height": 150,
    "goals": "Флирт",
    "body_type": "Худое",
}


@pytest.fixture()
async def user(async_client: AsyncClient):
    """Test user."""
    response = await async_client.post(
        app.url_path_for("register:register"),
        json=user_data,
    )
    return AuthUser(**response.json())


@pytest.fixture()
async def authorised_cookie(user: AuthUser):
    """Cookie of authorized user."""
    jwt = await get_jwt_strategy().write_token(user)
    return {"mir": jwt}


@pytest.fixture()
async def user2(async_client: AsyncClient):
    """Test user."""
    response = await async_client.post(
        app.url_path_for("register:register"),
        json=user2_data,
    )
    return AuthUser(**response.json())


@pytest.fixture()
async def user3(async_client: AsyncClient):
    """Test user."""
    response = await async_client.post(
        app.url_path_for("register:register"),
        json=user3_data,
    )
    return AuthUser(**response.json())


@pytest.fixture()
async def questionary(get_async_session: AsyncSession, user2: AuthUser):
    """User questionary."""
    user_questionary_data["user_id"] = user2.id
    async with get_async_session as db:
        questionary = UserQuestionnaire(**user_questionary_data)
        db.add(questionary)
        await db.commit()
    return questionary


@pytest.fixture()
async def match(get_async_session: AsyncSession, user: AuthUser, user2: AuthUser):
    async with get_async_session as db:
        match = Match(
            user1_id=user.id,
            user2_id=user2.id,
        )
        db.add(match)
        await db.commit()
    return match


@pytest.fixture()
async def match1(get_async_session: AsyncSession, user2: AuthUser, user3: AuthUser):
    async with get_async_session as db:
        match = Match(
            user1_id=user3.id,
            user2_id=user2.id,
        )
        db.add(match)
        await db.commit()
    return match


@pytest.fixture()
async def match2(get_async_session: AsyncSession, user2: AuthUser, user3: AuthUser):
    async with get_async_session as db:
        match = Match(
            user1_id=user2.id,
            user2_id=user3.id,
        )
        db.add(match)
        await db.commit()
    return match


@pytest.fixture()
async def like1(get_async_session: AsyncSession, user: AuthUser, user2: AuthUser):
    async with get_async_session as db:
        like = UserLike(
            user_id=user.id,
            liked_user_id=user2.id,
        )
        db.add(like)
        await db.commit()
    return like


@pytest.fixture()
async def like2(get_async_session: AsyncSession, user: AuthUser, user2: AuthUser):
    async with get_async_session as db:
        like = UserLike(
            user_id=user2.id,
            liked_user_id=user.id,
        )
        db.add(like)
        await db.commit()
    return like
