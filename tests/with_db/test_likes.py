import uuid

from dirty_equals import IsDatetime, IsInt
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import add_user
from src.auth.schemas import UserCreateInput, UserCreateOutput


async def test_like_user(async_client: AsyncClient, get_async_session: AsyncSession):
    user = UserCreateInput(email="lol@kek.com", password="password")
    user_to_like = UserCreateInput(email="lol2@kek2.com", password="password")

    user_db = UserCreateOutput.from_orm(await add_user(user, get_async_session))
    user_to_like_db = UserCreateOutput.from_orm(
        await add_user(user_to_like, get_async_session),
    )
    data = {"user_id": str(user_db.id), "liked_user_id": str(user_to_like_db.id)}

    response: Response = await async_client.post("/api/v1/likes", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": IsInt,
        "user_id": str(user_db.id),
        "liked_user_id": str(user_to_like_db.id),
        "created_at": IsDatetime(iso_string=True),
    }


async def test_like_wrong_user(
    async_client: AsyncClient,
    get_async_session: AsyncSession,
):
    data = {"user_id": str(uuid.uuid4()), "liked_user_id": str(uuid.uuid4())}

    response: Response = await async_client.post("/api/v1/likes", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "bad user id"
