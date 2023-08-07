from dirty_equals import Contains, IsFalseLike, IsInt, IsTrueLike
from httpx import AsyncClient


async def test_register(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/register", json={
        "email": "test_user@mail.com", "password": "test"})
    assert response.status_code == IsInt(exactly=201)


async def test_login(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/login",
                                       data={"username": "test_user@mail.com",
                                             "password": "test"})
    token = response.cookies.get("fastapiusersauth")
    assert response.status_code == IsInt(exactly=204)
    assert token == IsTrueLike


async def test_login_bad_credentials(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/login",
                                       data={"username": "test@m.com",
                                             "password": "string"})
    token = response.cookies.get("fastapiusersauth")

    assert response.text == Contains('{"detail":"LOGIN_BAD_CREDENTIALS"}')
    assert response.status_code == IsInt(exactly=400)
    assert token == IsFalseLike


async def test_logout_unauthorized(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/logout")
    assert response.text == Contains('{"detail":"Unauthorized"}')
    assert response.status_code == IsInt(exactly=401)
