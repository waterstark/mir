from dirty_equals import IsUUID
from fastapi import status
from httpx import AsyncClient


class TestUser:
    """Тесты на пользователя."""
    async def test_user_registration(self, async_client: AsyncClient):
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

    async def test_user_registration_with_incorrect_data(
                self,
                async_client: AsyncClient,
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
