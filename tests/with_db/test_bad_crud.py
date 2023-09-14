from fastapi import status
from httpx import AsyncClient

from src.auth.models import AuthUser
from src.questionnaire.models import UserQuestionnaire


async def test_create_questionnaire_bad_credentials(
    async_client: AsyncClient,
    user: AuthUser,
    questionary: UserQuestionnaire,
):
    questionnaire_data = {
        "firstname": "string",
        "lastname": "string",
        "gender": "Male",
        "photo": "string",
        "country": "string",
        "city": "string",
        "about": "string",
        "passion": "Музыка",
        "height": 0,
        "goals": "Дружба",
        "body_type": "Худое",
        "user_id": questionary.user_id,
    }
    response = await async_client.post(
        "api/v1/questionnaire",
        json=questionnaire_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == f"Объект уже существует в базе данных!!!{questionary.firstname}"
    )
