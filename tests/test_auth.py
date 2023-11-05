from typing import TYPE_CHECKING

import pytest
from async_asgi_testclient import TestClient
from dirty_equals import IsUUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import get_user_profile
from src.auth.models import AuthUser
from src.main import app
from tests.fixtures import user_data

if TYPE_CHECKING:
    from src.auth.schemas import UserProfile


class TestUser:
    """Тесты на пользователя."""

    async def test_user_registration(self, async_client: TestClient):
        """Тест - создание пользователя."""
        user_data = {
            "email": "user@mail.ru",
            "password": "password",
        }
        response = await async_client.post(
            app.url_path_for("register:register"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": IsUUID,
            "email": user_data.get("email"),
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        }

    async def test_user_registration_with_same_email(
        self,
        user: AuthUser,
        async_client: TestClient,
    ):
        """Тест - создание уже существующего пользователя."""
        response = await async_client.post(
            app.url_path_for("register:register"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_user_registration_with_incorrect_data(
        self,
        async_client: TestClient,
    ):
        """Тест - создание пользователя: некорректные данные."""
        wrong_data = {
            "email": "not_email",
            "password": "password",
        }
        response = await async_client.post(
            app.url_path_for("register:register"),
            json=wrong_data,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_login(
        self,
        user: AuthUser,
        async_client: TestClient,
    ):
        """Тест - авторизация зарегистрированного пользователя."""
        response = await async_client.post(
            app.url_path_for("auth:jwt.login"),
            form=[
                ("username", user.email),
                ("password", user_data.get("password")),
            ],
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_login_wrong_password(
        self,
        user: AuthUser,
        async_client: TestClient,
    ):
        """Тест - вход c неправильным паролем."""
        response = await async_client.post(
            app.url_path_for("auth:jwt.login"),
            form=[
                ("username", user.email),
                ("password", "wrong_password"),
            ],
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_logout(
        self,
        authorised_cookie: dict,
        async_client: TestClient,
    ):
        """Тест - logout авторизованного пользователя."""
        response = await async_client.post(
            app.url_path_for("auth:jwt.logout"),
            cookies=authorised_cookie,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestUserProfile:
    """Тесты профиля пользователя."""

    async def test_get_user_profile(
        self,
        user: AuthUser,
        authorised_cookie: dict,
        async_client: TestClient,
        get_async_session: AsyncSession,
    ):
        """Тест - получение профиля пользователя."""
        profile: UserProfile = await get_user_profile(
            user=user,
            session=get_async_session,
        )
        response = await async_client.get(
            app.url_path_for("get_profile"),
            cookies=authorised_cookie,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "subscriber": profile.subscriber,
            "search_range_min": profile.search_range_min,
            "search_range_max": profile.search_range_max,
            "search_age_min": profile.search_age_min,
            "search_age_max": profile.search_age_max,
        }

    async def test_update_user_profile(
        self,
        user: AuthUser,
        authorised_cookie: dict,
        async_client: TestClient,
        get_async_session: AsyncSession,
    ):
        """Тест - обновление профиля пользователя."""
        data = {
            "search_range_min": 0,
            "search_range_max": 100,
            "search_age_min": 18,
            "search_age_max": 80,
        }
        response = await async_client.patch(
            app.url_path_for("get_profile"),
            cookies=authorised_cookie,
            json=data,
        )
        assert response.status_code == status.HTTP_200_OK
        profile: UserProfile = await get_user_profile(
            user=user,
            session=get_async_session,
        )
        assert response.json() == {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "subscriber": profile.subscriber,
            "search_range_min": data.get("search_range_min"),
            "search_range_max": data.get("search_range_max"),
            "search_age_min": data.get("search_age_min"),
            "search_age_max": data.get("search_age_max"),
        }

    @pytest.mark.parametrize(
        ("age_min", "age_max", "range_min", "range_max"),
        [
            (17, 60, 0, 999),
            (18, 100, 0, 999),
            (18, 60, -1, 999),
            (18, 60, 0, 1000),
            (18, 60, 999, 0),
            (60, 18, 0, 999),
        ],
    )
    async def test_update_profile_with_wrong_data(
        self,
        age_min: int,
        age_max: int,
        range_min: int,
        range_max: int,
        authorised_cookie: dict,
        async_client: TestClient,
    ):
        """Тест - обновление профиля пользователя."""
        wrong_data = {
            "search_range_min": range_min,
            "search_range_max": range_max,
            "search_age_min": age_min,
            "search_age_max": age_max,
        }
        response = await async_client.patch(
            app.url_path_for("get_profile"),
            cookies=authorised_cookie,
            json=wrong_data,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
