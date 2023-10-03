import uuid

from dirty_equals import IsDatetime, IsUUID
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser


async def test_like_user(
    async_client: AsyncClient,
    get_async_session: AsyncSession,
    user: AuthUser,
    user2: AuthUser,
):
    data = {"user_id": str(user.id), "liked_user_id": str(user2.id), "is_liked": True}

    response: Response = await async_client.post("/api/v1/likes", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": IsUUID,
        "user_id": str(user.id),
        "liked_user_id": str(user2.id),
        "created_at": IsDatetime(iso_string=True),
        "is_liked": True,
    }


async def test_like_wrong_user(
    async_client: AsyncClient,
    get_async_session: AsyncSession,
):
    data = {"user_id": str(uuid.uuid4()), "liked_user_id": str(uuid.uuid4())}

    response: Response = await async_client.post("/api/v1/likes", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "bad user id"
