import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from async_asgi_testclient import TestClient
from dirty_equals import IsInt, IsUUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.crud import get_user_profile
from src.auth.models import AuthUser
from src.main import app

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
            "/api/v1/auth/register",
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
        async_client: TestClient,
    ):
        """Тест - создание уже существующего пользователя."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@mail.ru",
                "password": "password",
            },
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
            "/api/v1/auth/register",
            json=wrong_data,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_cookies_after_register(
        self,
        async_client: TestClient,
    ) -> None:
        """Тест - проверка кук после создания пользователя."""
        cookies_data = auth_utils.decode_jwt(async_client.cookie_jar["mir"].value)
        assert cookies_data == {
            "email": "user@mail.ru",
            "exp": IsInt,
            "sub": IsUUID,
            "type": "mir",
        }
        expires = (datetime.utcnow() + timedelta(minutes=14)).timestamp()
        assert int(cookies_data["exp"]) > int(expires)

    async def test_login_wrong_password(
        self,
        async_client: TestClient,
    ):
        """Тест - вход c неправильным паролем."""
        async_client.cookie_jar.clear()
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@mail.ru",
                "password": "wrong_password",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert async_client.cookie_jar.get("mir") is None

    async def test_login(
        self,
        async_client: TestClient,
    ):
        """Тест - авторизация зарегистрированного пользователя."""
        async_client.cookie_jar.clear()
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@mail.ru",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert auth_utils.decode_jwt(async_client.cookie_jar["mir"].value) == {
            "email": "user@mail.ru",
            "exp": IsInt,
            "sub": IsUUID,
            "type": "mir",
        }

    async def test_refresh_token(
        self,
        async_client: TestClient,
    ) -> None:
        """Тест - перевыпуска access_token по refresh_token."""
        old_access_token = async_client.cookie_jar["mir"].value
        old_refresh_token = async_client.cookie_jar["rsmir"].value

        await asyncio.sleep(1)

        response = await async_client.get(
            "/api/v1/auth/refresh",
            cookies={"rsmir": old_refresh_token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies["mir"] != old_access_token
        assert response.cookies["rsmir"] != old_refresh_token

    async def test_refresh_token_without_token(
        self,
        async_client: TestClient,
    ) -> None:
        """Тест обновления токенов без refresh_token."""

        response = await async_client.get(
            "/api/v1/auth/refresh",
            cookies={"rsmir": ""},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": "Not authenticated",
        }

    async def test_refresh_token_with_incorrect_token(
        self,
        async_client: TestClient,
    ) -> None:
        """Тест обновления токенов c некорректным токеном."""
        response = await async_client.get(
            "/api/v1/auth/refresh",
            cookies={"rsmir": "some.incorrect.refresh.token"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "could not refresh access token",
        }

    async def test_logout(
        self,
        async_client: TestClient,
    ):
        """Тест - logout авторизованного пользователя."""
        response = await async_client.get(
            "/api/v1/auth/logout",
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.cookies.get("mir") is None
        assert response.cookies.get("rsmir") is None

    async def test_expired_access_token(
        self,
        async_client: TestClient,
    ):
        """Тест - просроченный токен доступа."""
        with mock.patch("src.config.settings.ACCESS_TOKEN_EXPIRES_IN", new=0.01):
            await async_client.post(
                "/api/v1/auth/login",
                json={
                    "email": "user@mail.ru",
                    "password": "password",
                },
            )
            await asyncio.sleep(0.5)
            response = await async_client.get(
                "/api/v1/users/me",
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_expired_refresh_token(
        self,
        async_client: TestClient,
    ):
        """Тест - просроченный рефреш токен."""
        with mock.patch("src.config.settings.REFRESH_TOKEN_EXPIRES_IN", new=0.01):
            await async_client.post(
                "/api/v1/auth/login",
                json={
                    "email": "user@mail.ru",
                    "password": "password",
                },
            )
            await asyncio.sleep(0.5)
            response = await async_client.get(
                "/api/v1/auth/refresh",
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST


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

    async def test_get_user_profile_without_token(
        self,
        async_client: TestClient,
    ):
        """Тест - получение профиля пользователя без токена."""
        response = await async_client.get(
            app.url_path_for("get_profile"),
            cookies={},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        """Тест - получение профиля пользователя c неправильным токеном."""
        response = await async_client.get(
            app.url_path_for("get_profile"),
            cookies={"mir": "some.kind.of.incorrect.cookies"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

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

    async def test_update_user_profile_without_token(
        self,
        async_client: TestClient,
    ):
        """Тест - обновление профиля пользователя без токена."""
        data = {
            "search_range_min": 0,
            "search_range_max": 100,
            "search_age_min": 18,
            "search_age_max": 80,
        }
        response = await async_client.patch(
            app.url_path_for("get_profile"),
            json=data,
            cookies={},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        """Тест - обновление профиля пользователя c неправильным токеном."""
        response = await async_client.patch(
            app.url_path_for("get_profile"),
            json=data,
            cookies={"mir": "some.kind.of.incorrect.cookies"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

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
