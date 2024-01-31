from async_asgi_testclient import TestClient
from dirty_equals import IsUUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.likes.models import UserLike
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
    }
    response = await async_client.post(
        "/api/v1/questionnaire",
        json=questionnaire_data,
        cookies={"mir": async_client.cookie_jar.get("mir")},
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
    user: AuthUser,
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
    }
    user_jwt = async_client.cookie_jar.get("mir")
    response = await async_client.post(
        "/api/v1/questionnaire",
        json=questionnaire_data,
        cookies={"mir": user_jwt},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    questionary = await async_client.get(
        "/api/v1/questionnaire/get_my_quest",
        cookies={"mir": user_jwt},
    )
    assert (
        response.json()["detail"]
        == f"Объект уже существует в базе данных!!!{questionary.json()['firstname']}"
    )


async def test_get_quest_authenticated_user(
    async_client: TestClient,
    user: AuthUser,
):
    response = await async_client.get(
        "/api/v1/questionnaire/get_my_quest",
        cookies={"mir": async_client.cookie_jar.get("mir")},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
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
        "id": IsUUID,
    }


async def test_logic_for_reusing_questionnaires(
    async_client: TestClient,
    user2: AuthUser,
    authorised_cookie_user2: dict,
    like3: UserLike,
    questionary: UserQuestionnaire,
    questionary_user3: UserQuestionnaire,
):
    response = await async_client.get(
        "/api/v1/questionnaire/list/0",
        cookies=authorised_cookie_user2,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


async def test_update_quest(
    async_client: TestClient,
    questionary: UserQuestionnaire,
    user2: AuthUser,
    authorised_cookie_user2: dict,
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
    }

    response = await async_client.patch(
        f"/api/v1/questionnaire/{questionary.id}",
        json=updated_data,
        cookies=authorised_cookie_user2,
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
    user2: AuthUser,
    authorised_cookie_user2: dict,
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


async def test_create_questionnaire_without_token(
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
    }

    """Without cookies."""

    response = await async_client.post(
        "/api/v1/questionnaire",
        json=questionnaire_data,
        cookies={},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    """Incorrect cookies."""

    response = await async_client.post(
        "/api/v1/questionnaire",
        json=questionnaire_data,
        cookies={"mir": "some.kind.of.incorrect.cookies"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_questionnaires_without_token(
    async_client: TestClient,
):
    response = await async_client.get(
        "/api/v1/questionnaire/get_my_quest",
        cookies={},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await async_client.get(
        "/api/v1/questionnaire/list/0",
        cookies={},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_update_or_delete_quest_without_token(
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
    }

    response = await async_client.patch(
        f"/api/v1/questionnaire/{questionary.id}",
        json=updated_data,
        cookies={},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await async_client.delete(
        f"/api/v1/questionnaire/{questionary.id}",
        cookies={},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
