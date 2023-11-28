from async_asgi_testclient import TestClient
from dirty_equals import IsUUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.questionnaire.crud import get_questionnaire
from src.questionnaire.models import UserQuestionnaire


async def test_create_questionnaire(
    async_client: TestClient,
    user: AuthUser,
):
    questionnaire_data = {
        "firstname": "string",
        "lastname": "string",
        "gender": "Male",
        "photo": "string",
        "country": "string",
        "city": "string",
        "about": "string",
        "hobbies": [{"hobby_name": "string"}],
        "height": 0,
        "goals": "Дружба",
        "body_type": "Худое",
        "age": 20,
        "user_id": user.id,
    }
    response = await async_client.post(
        "/api/v1/questionnaire",
        json=questionnaire_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": IsUUID,
        "firstname": "string",
        "lastname": "string",
        "gender": "Male",
        "photo": "string",
        "country": "string",
        "city": "string",
        "about": "string",
        "hobbies": [{"hobby_name": "string"}],
        "height": 0,
        "goals": "Дружба",
        "body_type": "Худое",
        "age": 20,
        "user_id": IsUUID,
    }
    assert response.json()["user_id"] == str(user.id)


async def test_create_questionnaire_bad_credentials(
    async_client: TestClient,
    user2: AuthUser,
    questionary: UserQuestionnaire,
):
    questionnaire_data = {
        "firstname": "s123123tring",
        "lastname": "string",
        "gender": "Male",
        "photo": "string",
        "country": "string",
        "city": "string",
        "about": "string",
        "hobbies": [{"hobby_name": "string"}],
        "height": 0,
        "goals": "Дружба",
        "body_type": "Худое",
        "age": 20,
        "user_id": questionary.user_id,
    }
    response = await async_client.post(
        "/api/v1/questionnaire",
        json=questionnaire_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == f"Объект уже существует в базе данных!!!{questionary.firstname}"
    )


async def test_update_quest(
    async_client: TestClient,
    questionary: UserQuestionnaire,
    user2: AuthUser,
):
    updated_data = {
        "firstname": "string",
        "lastname": "string",
        "gender": "Female",
        "photo": "string",
        "country": "string",
        "city": "string",
        "about": "string",
        "hobbies": [
            {
                "hobby_name": "qwewasd",
            },
            {
                "hobby_name": "asidpas",
            },
        ],
        "height": 0,
        "goals": "Флирт",
        "body_type": "Полное",
        "age": 20,
        "user_id": user2.id,
    }

    response = await async_client.patch(
        f"/api/v1/questionnaire/{questionary.id}",
        json=updated_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": IsUUID,
        "firstname": "string",
        "lastname": "string",
        "gender": "Female",
        "photo": "string",
        "country": "string",
        "city": "string",
        "about": "string",
        "hobbies": [
            {
                "hobby_name": "qwewasd",
            },
            {
                "hobby_name": "asidpas",
            },
        ],
        "height": 0,
        "goals": "Флирт",
        "body_type": "Полное",
        "age": 20,
        "user_id": IsUUID,
    }
    assert response.json()["user_id"] == str(user2.id)


async def test_delete_quest(
    async_client: TestClient,
    questionary: UserQuestionnaire,
    authorised_cookie_user2: dict,
    user2: AuthUser,
    get_async_session: AsyncSession,
):
    response = await async_client.delete(
        f"/api/v1/questionnaire/{questionary.id}",
        cookies=authorised_cookie_user2,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response_check = await get_questionnaire(
        user_id=user2.id,
        session=get_async_session,
    )
    assert response_check is None
