from fastapi import status
from httpx import AsyncClient

from src.auth.models import AuthUser
from src.questionnaire.models import UserQuestionnaire


async def test_get_list_questionnaire(async_client: AsyncClient):
    resp = await async_client.get("api/v1/quest")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_questionnaire(async_client: AsyncClient, user: AuthUser):
    questionnaire_data = {
        "id": str(user.id),
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
    response = await async_client.post(
        "api/v1/quest",
        json=questionnaire_data,
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_quest(
    async_client: AsyncClient,
    questionary: UserQuestionnaire,
):
    updated_data = {
        "id": str(questionary.id),
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
    response = await async_client.patch(
        f"api/v1/quest/{questionary.id}",
        json=updated_data,
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_quest(
    async_client: AsyncClient,
    questionary: UserQuestionnaire,
):
    response = await async_client.delete(f"api/v1/quest/{questionary.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
