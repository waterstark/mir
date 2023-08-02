import pytest
from httpx import AsyncClient


@pytest.mark.asyncio()
async def test_get_list_questionnaire(async_client: AsyncClient):
    resp = await async_client.get("/quest/all-quest")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio()
async def test_create_questionnaire(async_client: AsyncClient):
    user_questionnaire = {
        "id": "d5c5f699-0f9e-4499-af2b-f0723349e9f9",
        "firstname": "nikita",
        "lastname": "pupkin",
        "gender": "Male",
        "photo": "False",
        "country": "False",
        "city": "False",
        "about": "False",
        "passion": "Путешествия",
        "height": 150,
        "goals": "Флирт",
        "body_type": "Худое",
    }
    resp = await async_client.post(
        "/quest/add-quest",
        json=user_questionnaire,
    )
    assert resp.status_code == 201


@pytest.mark.asyncio()
async def test_update_quest(async_client: AsyncClient):
    update_user_quest = {
        "id": "d5c5f699-0f9e-4499-af2b-f0723349e9f9",
        "firstname": "nikita",
        "lastname": "pupkin",
        "gender": "Female",
        "photo": "False",
        "country": "False",
        "city": "False",
        "about": "False",
        "passion": "Фотография",
        "height": 145,
        "goals": "Дружба",
        "body_type": "Полное",
    }
    resp = await async_client.patch(
        "/quest/update/{d5c5f699-0f9e-4499-af2b-f0723349e9f9}",
        json=update_user_quest)
    assert resp.status_code == 200


@pytest.mark.asyncio()
async def test_delete_quest(async_client: AsyncClient):
    resp = await async_client.delete("/quest/{d5c5f699-0f9e-4499-af2b-f0723349e9f9}")
    assert resp.status_code == 204
