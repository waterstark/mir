import asyncio
import uuid

from dirty_equals import IsDatetime, IsUUID
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.matches.crud import get_match_by_user_ids
from src.questionnaire.crud import get_rate
from src.questionnaire.models import UserQuestionnaire


async def test_match_creation_after_double_like(
    async_client: AsyncClient,
    authorised_cookie_user2: dict,
    user2: AuthUser,
    authorised_cookie_user3: dict,
    questionary: UserQuestionnaire,
    user3: AuthUser,
    get_async_session: AsyncSession,
    questionary_user3: UserQuestionnaire,
):
    """Проверка корректного создания match после взаимного лайка двух пользователей.
    """
    data1 = {"liked_user_id": str(user2.id), "is_liked": True}
    data2 = {"liked_user_id": str(user3.id), "is_liked": True}

    response1: Response = await async_client.post("/api/v1/likes", json=data1, cookies=authorised_cookie_user3)
    response2: Response = await async_client.post("/api/v1/likes", json=data2, cookies=authorised_cookie_user2)

    assert response1.status_code == status.HTTP_201_CREATED
    assert response2.status_code == status.HTTP_201_CREATED

    await asyncio.sleep(0.05)
    match = await get_match_by_user_ids(get_async_session, user1_id=user3.id, user2_id=user2.id)

    assert match is not None


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
