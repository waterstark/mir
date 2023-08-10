import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import get_jwt_strategy
from src.auth.models import AuthUser
from src.main import app
from src.questionnaire.models import UserQuestionnaire

user_data = {
    "email": "test_user@server.com",
    "password": "pass",
}

questionary_data = {
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
async def questionary(get_async_session: AsyncSession, user: AuthUser):
    """User questionary."""
    questionary_data["id"] = user.id
    async with get_async_session as db:
        questionary = UserQuestionnaire(**questionary_data)
        db.add(questionary)
        await db.commit()
    return questionary


@pytest.fixture()
async def authorised_cookie(user: AuthUser):
    """Cookie of authorized user."""
    jwt = await get_jwt_strategy().write_token(user)
    return {"mir": jwt}
