from datetime import datetime

import pytest
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.likes.models import UserLike
from src.matches.models import Match
from src.questionnaire.models import UserQuestionnaire, UserQuestionnaireHobby

"""Without that tests will die, sa cant work with date and pytest same time normaly(kostil)"""
date_string = "2004-02-14"
datetime_object = datetime.strptime(date_string, "%Y-%m-%d")
date_object = datetime_object.date()

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
    "goals": "Дружба",
    "height": 150,
    "sport": "He занимаюсь",
    "alcohol": "He пью",
    "smoking": "Курю",
    "birthday": date_object,
}

user3_questionary_data = {
    "firstname": "Anton",
    "lastname": "Pupkin",
    "gender": "Female",
    "photo": "False",
    "country": "False",
    "city": "False",
    "about": "False",
    "goals": "Дружба",
    "height": 150,
    "sport": "He занимаюсь",
    "alcohol": "He пью",
    "smoking": "Курю",
    "birthday": date_object,
}

hobbies_dict = {
    "hobbies": [
        {"hobby_name": "qwe"},
        {"hobby_name": "asd"},
    ],
}


@pytest.fixture(scope="module")
async def user(async_client: TestClient) -> AuthUser:
    """Test user."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user_data,
    )
    return AuthUser(**response.json())


@pytest.fixture(scope="module")
async def user2(async_client: TestClient) -> AuthUser:
    """Test user."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user2_data,
    )
    return AuthUser(**response.json())


@pytest.fixture(scope="module")
async def user3(async_client: TestClient) -> AuthUser:
    """Test user."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user3_data,
    )
    return AuthUser(**response.json())


@pytest.fixture(scope="module")
async def authorised_cookie(user: AuthUser, async_client: TestClient) -> dict:
    """Cookie of authorized user."""
    await async_client.post(
        "/api/v1/auth/login",
        json=user_data,
    )
    jwt = async_client.cookie_jar.get("mir")
    return {"mir": jwt}


@pytest.fixture(scope="module")
async def authorised_cookie_user2(user2: AuthUser, async_client: TestClient) -> dict:
    """Cookie of authorized user."""
    await async_client.post(
        "/api/v1/auth/login",
        json=user2_data,
    )
    jwt = async_client.cookie_jar.get("mir")
    return {"mir": jwt}


@pytest.fixture(scope="module")
async def authorised_cookie_user3(user3: AuthUser, async_client: TestClient) -> dict:
    """Cookie of authorized user."""
    await async_client.post(
        "/api/v1/auth/login",
        json=user3_data,
    )
    jwt = async_client.cookie_jar.get("mir")
    return {"mir": jwt}


@pytest.fixture(scope="module")
async def questionary(get_async_session: AsyncSession, user2: AuthUser) -> UserQuestionnaire:
    """User questionary."""
    user_questionary_data["user_id"] = user2.id
    async with get_async_session as db:
        questionnaire = UserQuestionnaire(**user_questionary_data)
        _hobbies: list = hobbies_dict["hobbies"]
        for hobby in _hobbies:
            hobby_obj = UserQuestionnaireHobby(hobby_name=hobby["hobby_name"])
            questionnaire.hobbies.append(hobby_obj)
        db.add(questionnaire)
        await db.commit()
    return questionnaire


@pytest.fixture(scope="module")
async def questionary_user3(get_async_session: AsyncSession, user3: AuthUser) -> UserQuestionnaire:
    """User questionary."""
    user3_questionary_data["user_id"] = user3.id
    async with get_async_session as db:
        questionary_user3 = UserQuestionnaire(**user3_questionary_data)
        _hobbies: list = hobbies_dict["hobbies"]
        for hobby in _hobbies:
            hobby_obj = UserQuestionnaireHobby(hobby_name=hobby["hobby_name"])
            questionary_user3.hobbies.append(hobby_obj)
        db.add(questionary_user3)
        await db.commit()
    return questionary_user3


@pytest.fixture(scope="module")
async def match(get_async_session: AsyncSession, user: AuthUser, user2: AuthUser) -> Match:
    async with get_async_session as db:
        match = Match(
            user1_id=user.id,
            user2_id=user2.id,
        )
        db.add(match)
        await db.commit()
    return match


@pytest.fixture(scope="module")
async def match1(get_async_session: AsyncSession, user2: AuthUser, user3: AuthUser) -> Match:
    async with get_async_session as db:
        match = Match(
            user1_id=user3.id,
            user2_id=user2.id,
        )
        db.add(match)
        await db.commit()
    return match


@pytest.fixture(scope="module")
async def match2(get_async_session: AsyncSession, user2: AuthUser, user3: AuthUser) -> Match:
    async with get_async_session as db:
        match = Match(
            user1_id=user2.id,
            user2_id=user3.id,
        )
        db.add(match)
        await db.commit()
    return match


@pytest.fixture(scope="module")
async def like1(get_async_session: AsyncSession, user: AuthUser, user2: AuthUser) -> UserLike:
    async with get_async_session as db:
        like = UserLike(
            user_id=user.id,
            liked_user_id=user2.id,
        )
        db.add(like)
        await db.commit()
    return like


@pytest.fixture(scope="module")
async def like2(get_async_session: AsyncSession, user: AuthUser, user2: AuthUser) -> UserLike:
    async with get_async_session as db:
        like = UserLike(
            user_id=user2.id,
            liked_user_id=user.id,
        )
        db.add(like)
        await db.commit()
    return like


@pytest.fixture(scope="module")
async def like3(get_async_session: AsyncSession, user3: AuthUser, user2: AuthUser) -> UserLike:
    async with get_async_session as db:
        like = UserLike(
            user_id=user2.id,
            liked_user_id=user3.id,
        )
        db.add(like)
        await db.commit()
    return like
