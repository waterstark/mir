import uuid

from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import add_user
from src.auth.schemas import UserCreateInput, UserCreateOutput


async def test_like_user(async_client: AsyncClient, session: AsyncSession):
    user = UserCreateInput(email="lol@kek.com", password="password")
    user_to_like = UserCreateInput(email="lol2@kek2.com", password="password")

    user_db = UserCreateOutput.from_orm(await add_user(user, session))
    user_to_like_db = UserCreateOutput.from_orm(await add_user(user_to_like, session))
    data = {"user_id": str(user_db.id), "liked_user_id": str(user_to_like_db.id)}

    response: Response = await async_client.post("/api/v1/like", json=data)

    assert response.status_code == 200
    assert response.json()["id"] is not None


async def test_like_wrong_user(async_client: AsyncClient, session: AsyncSession):
    data = {"user_id": str(uuid.uuid4()), "liked_user_id": str(uuid.uuid4())}

    response: Response = await async_client.post("/api/v1/like", json=data)

    assert response.status_code == 404
    assert response.json()["detail"] == "bad user id"
