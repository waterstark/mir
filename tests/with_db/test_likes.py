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
