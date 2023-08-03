import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.questionnaire.models import UserQuestionnaire

user_data = {
    "email": "test_user@server.com",
    "hashed_password": "pass",
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
async def user(get_async_session: AsyncSession):
    async with get_async_session as db:
        user = AuthUser(**user_data)
        db.add(user)
        await db.commit()
    return user


@pytest.fixture()
async def questionary(get_async_session: AsyncSession, user: AuthUser):
    questionary_data["id"] = user.id
    async with get_async_session as db:
        questionary = UserQuestionnaire(**questionary_data)
        db.add(questionary)
        await db.commit()
    return questionary
