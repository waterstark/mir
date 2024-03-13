from dirty_equals import IsDatetime, IsUUID
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.questionnaire.models import UserQuestionnaire


async def test_like_user(
    async_client: AsyncClient,
    authorised_cookie: dict,
    user3: AuthUser,
    questionary_user3: UserQuestionnaire,
    get_async_session: AsyncSession,
):
    """Проверка корректного выставления лайка.
    """

    data = {"liked_user_id": str(user3.id), "is_liked": True}

    response: Response = await async_client.post("/api/v1/likes", json=data, cookies=authorised_cookie)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": IsUUID,
        "liked_user_id": str(user3.id),
        "created_at": IsDatetime(iso_string=True),
        "is_liked": True,
    }

async def test_skip_user(
    async_client: AsyncClient,
    authorised_cookie: dict,
    user2: AuthUser,
    questionary: UserQuestionnaire,
    get_async_session: AsyncSession,
):
    """Проверка корректного скипа.
    """

    data = {"liked_user_id": str(user2.id), "is_liked": False}

    response: Response = await async_client.post("/api/v1/likes", json=data, cookies=authorised_cookie)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": IsUUID,
        "liked_user_id": str(user2.id),
        "created_at": IsDatetime(iso_string=True),
        "is_liked": False,
    }