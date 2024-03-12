import asyncio
import uuid

from dirty_equals import IsDatetime, IsUUID
from fastapi import status
from httpx import AsyncClient, Response

from src.auth.models import AuthUser
from src.questionnaire.models import UserQuestionnaire


async def test_like_user(
    async_client: AsyncClient,
    authorised_cookie: dict,
    user3: AuthUser,
    questionary_user3: UserQuestionnaire,
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

async def test_like_wrong_user(
    async_client: AsyncClient,
    authorised_cookie: dict,
    user3: AuthUser,
    questionary_user3: UserQuestionnaire,
):
    """Проверка того, что пользователь не может лайкнуть несуществующего пользователя.
    """
    data = {"liked_user_id": str(uuid.uuid4())}

    response: Response = await async_client.post("/api/v1/likes", json=data, cookies=authorised_cookie)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "questionanire not found"


async def test_self_like(
    async_client: AsyncClient,
    authorised_cookie: dict,
    user3: AuthUser,
    questionary_user3: UserQuestionnaire,
):
    """Проверка того, что пользователь не может лайкнуть себя.
    """
    data = {"liked_user_id": str(user3.id)}

    response: Response = await async_client.post("/api/v1/likes", json=data, cookies=authorised_cookie)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "bad user id"

async def test_like_user_without_token(
    async_client: AsyncClient,
    user2: AuthUser,
):
    """Проверка выставления лайка без токена или c неправильным токеном.
    """
    data = {"liked_user_id": str(user2.id), "is_liked": True}

    response: Response = await async_client.post("/api/v1/likes", json=data, cookies={})

    assert response.status_code == status.HTTP_403_FORBIDDEN

    response: Response = await async_client.post(
        "/api/v1/likes",
        json=data,
        cookies={"mir": "some.kind.of.incorrect.cookies"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
