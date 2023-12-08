from typing import TYPE_CHECKING

import pytest
import orjson
from async_asgi_testclient import TestClient
from dirty_equals import IsUUID, IsStr, IsStr
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.util import MessageStatus, WSAction, WSStatus
from src.auth.crud import get_user_profile
from src.auth.models import AuthUser
from src.main import app
from tests.fixtures import user_data
from src.auth.models import AuthUser
from src.questionnaire.crud import get_questionnaire
from src.questionnaire.models import UserQuestionnaire


class TestAcceptance:
    """Тесты на поведение пользователя."""

    async def test_acceptance(self, async_client: TestClient, user: AuthUser,):

        """1. Регистрация двух пользователей."""
        """2. Создание анкет двух пользователей."""
        """3. Логины двух пользователей."""
        """4. Взаимные лайки двух пользователей."""
        """5. Проверка матча."""

        """Регистрация двух пользователей."""

        user_1_data = {
            "email": "user1@mail.ru",
            "password": "password",
        }
        response = await async_client.post(
            app.url_path_for("register:register"),
            json=user_1_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        created_user_1_id = response.json()["id"]
        assert response.json() == {
            "id": created_user_1_id,
            "email": user_1_data.get("email"),
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        }
        user_2_data = {
            "email": "user2@mail.ru",
            "password": "password",
        }
        response = await async_client.post(
            app.url_path_for("register:register"),
            json=user_2_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        created_user_2_id = response.json()["id"]
        assert response.json() == {
            "id": created_user_2_id,
            "email": user_2_data.get("email"),
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        }

        """Создание двух анкет."""

        questionnaire_1_data = {
            "firstname": "Антон",
            "lastname": "Суворов",
            "gender": "Male",
            "photo": "Фото",
            "country": "Россия",
            "city": "Питер",
            "about": "Мужичок",
            "hobbies": [{"hobby_name": "string"}],
            "height": 190,
            "goals": "Дружба",
            "body_type": "Худое",
            "age": 20,
            "user_id": created_user_1_id,
        }

        response = await async_client.post(
            "/api/v1/questionnaire",
            json=questionnaire_1_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": IsUUID,
            "firstname": questionnaire_1_data["firstname"],
            "lastname": questionnaire_1_data["lastname"],
            "gender": questionnaire_1_data["gender"],
            "photo": questionnaire_1_data["photo"],
            "country": questionnaire_1_data["country"],
            "city": questionnaire_1_data["city"],
            "about": questionnaire_1_data["about"],
            "hobbies": questionnaire_1_data["hobbies"],
            "height": questionnaire_1_data["height"],
            "goals": questionnaire_1_data["goals"],
            "body_type": questionnaire_1_data["body_type"],
            "age": questionnaire_1_data["age"],
            "user_id": created_user_1_id,
        }
        questionnaire_2_data = {
            "firstname": "Аня",
            "lastname": "Каренина",
            "gender": "Female",
            "photo": "Селфак",
            "country": "Россия",
            "city": "Питер",
            "about": "Баба",
            "hobbies": [{"hobby_name": "string"}],
            "height": 120,
            "goals": "Дружба",
            "body_type": "Худое",
            "age": 21,
            "user_id": created_user_2_id,
        }
        response = await async_client.post(
            "/api/v1/questionnaire",
            json=questionnaire_2_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
             "id": IsUUID,
            "firstname": questionnaire_2_data["firstname"],
            "lastname": questionnaire_2_data["lastname"],
            "gender": questionnaire_2_data["gender"],
            "photo": questionnaire_2_data["photo"],
            "country": questionnaire_2_data["country"],
            "city": questionnaire_2_data["city"],
            "about": questionnaire_2_data["about"],
            "hobbies": questionnaire_2_data["hobbies"],
            "height": questionnaire_2_data["height"],
            "goals": questionnaire_2_data["goals"],
            "body_type": questionnaire_2_data["body_type"],
            "age": questionnaire_2_data["age"],
            "user_id": created_user_2_id,
        }

        """Логин пользователя 1."""
        response = await async_client.post(
            app.url_path_for("auth:jwt.login"),
            form=[
                ("username", "user1@mail.ru"),
                ("password", "password"),
            ],
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        """Проверка анкет первым пользователем."""

        response = await async_client.get(
            f"/api/v1/questionnaire/10",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
            "id": IsUUID,
            "firstname": questionnaire_2_data["firstname"],
            "lastname": questionnaire_2_data["lastname"],
            "gender": questionnaire_2_data["gender"],
            "photo": questionnaire_2_data["photo"],
            "country": questionnaire_2_data["country"],
            "city": questionnaire_2_data["city"],
            "about": questionnaire_2_data["about"],
            "hobbies": questionnaire_2_data["hobbies"],
            "height": questionnaire_2_data["height"],
            "goals": questionnaire_2_data["goals"],
            "body_type": questionnaire_2_data["body_type"],
            "age": questionnaire_2_data["age"],
            "user_id": created_user_2_id,
        }]

        """Первый пользователь лайкает второго."""

        """Старый лайк"""

        """response = await async_client.post(
             f"/api/v1/users/{created_user_2_id}/like",
            form=[
                ("user_id", created_user_1_id)
            ])
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": IsUUID,
            "firstname": questionnaire_2_data["firstname"],
            "lastname": questionnaire_2_data["lastname"],
            "gender": questionnaire_2_data["gender"],
            "photo": questionnaire_2_data["photo"],
            "country": questionnaire_2_data["country"],
            "city": questionnaire_2_data["city"],
            "about": questionnaire_2_data["about"],
            "hobbies": questionnaire_2_data["hobbies"],
            "height": questionnaire_2_data["height"],
            "goals": questionnaire_2_data["goals"],
            "body_type": questionnaire_2_data["body_type"],
            "age": questionnaire_2_data["age"],
            "user_id": created_user_2_id,
            "is_match": False
        }"""

        """Новый лайк(Вроде Маки уже сделал)."""

        like_1 = {
            "liked_user_id": created_user_2_id,
            "is_liked": True
        }

        """Возможно поле is_like нужно будет убрать."""

        response = await async_client.post(
            f"/api/v1/likes",
            json = like_1,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "created_at": IsStr,
            "id": IsUUID,
            "liked_user_id": created_user_2_id,
            "is_liked": True
        }


        """Логин пользователя 2."""
        response = await async_client.post(
            app.url_path_for("auth:jwt.login"),
            form=[
                ("username", "user2@mail.ru"),
                ("password", "password"),
            ],
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        """Проверка анкет вторым пользователем."""

        response = await async_client.get(
            f"/api/v1/questionnaire/10",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
             "id": IsUUID,
            "firstname": questionnaire_1_data["firstname"],
            "lastname": questionnaire_1_data["lastname"],
            "gender": questionnaire_1_data["gender"],
            "photo": questionnaire_1_data["photo"],
            "country": questionnaire_1_data["country"],
            "city": questionnaire_1_data["city"],
            "about": questionnaire_1_data["about"],
            "hobbies": questionnaire_1_data["hobbies"],
            "height": questionnaire_1_data["height"],
            "goals": questionnaire_1_data["goals"],
            "body_type": questionnaire_1_data["body_type"],
            "age": questionnaire_1_data["age"],
            "user_id": created_user_1_id,
        }]

        """Второй пользователь лайкает первого."""

        """Старый лайк"""

        """response = await async_client.post(
            f"/api/v1/users/{created_user_1_id}/like",
            form=[
                ("user_id", str(created_user_2_id))
            ]
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": IsUUID,
            "firstname": questionnaire_1_data["firstname"],
            "lastname": questionnaire_1_data["lastname"],
            "gender": questionnaire_1_data["gender"],
            "photo": questionnaire_1_data["photo"],
            "country": questionnaire_1_data["country"],
            "city": questionnaire_1_data["city"],
            "about": questionnaire_1_data["about"],
            "hobbies": questionnaire_1_data["hobbies"],
            "height": questionnaire_1_data["height"],
            "goals": questionnaire_1_data["goals"],
            "body_type": questionnaire_1_data["body_type"],
            "age": questionnaire_1_data["age"],
            "user_id": IsUUID,
            "is_match": True
        }"""

        """Новый лайк(Вроде Маки уже сделал)."""

        like_2 = {
             "liked_user_id": created_user_1_id,
             "is_liked": True
        }

        """Возможно поле is_like нужно будет убрать."""

        response = await async_client.post(
            f"/api/v1/likes",
            json=like_2,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "created_at": IsStr,
            "id": IsUUID,
            "liked_user_id": created_user_1_id,
            "is_liked": True
        }

        """Проверка матча вторым пользователем."""

        response = await async_client.get(
            f"/api/v1/matches",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
            "id": IsUUID,
            "firstname": questionnaire_1_data["firstname"],
            "lastname": questionnaire_1_data["lastname"],
            "gender": questionnaire_1_data["gender"],
            "photo": questionnaire_1_data["photo"],
            "country": questionnaire_1_data["country"],
            "city": questionnaire_1_data["city"],
            "about": questionnaire_1_data["about"],
            "hobbies": questionnaire_1_data["hobbies"],
            "height": questionnaire_1_data["height"],
            "goals": questionnaire_1_data["goals"],
            "body_type": questionnaire_1_data["body_type"],
            "age": questionnaire_1_data["age"],
            "user_id": created_user_1_id,
            "is_match": True
        }]

    async def test_acceptance_with_chat(self, async_client: TestClient, user: AuthUser, ):
        """Тесты на чат между мользователями (пользователи взяты из предыдущего теста)."""

        """1. Логины двух пользователей."""
        """2. Получение различных id."""
        """3. Переписка (Работает только при подключении MongoDB)."""

        """Логин пользователя 1."""
        response = await async_client.post(
            app.url_path_for("auth:jwt.login"),
            form=[
                ("username", "user1@mail.ru"),
                ("password", "password"),
            ],
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        """Получаем id матча."""

        response = await async_client.get(
            f"/api/v1/matches",
        )
        created_match_id = response.json()[0]["id"]

        """Получаем id первого пользователя."""

        response = await async_client.get(
            f"/api/v1/users/me",
        )
        created_user_1_id = response.json()["id"]

        """Логин пользователя 2."""
        response = await async_client.post(
            app.url_path_for("auth:jwt.login"),
            form=[
                ("username", "user2@mail.ru"),
                ("password", "password"),
            ],
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        """Получаем id Второго пользователя."""

        response = await async_client.get(
            f"/api/v1/users/me",
        )
        created_user_2_id = response.json()["id"]

        """Создание сообщений первым пользователем."""

        msg = {"match_id": created_match_id, "text": "Пр, го встр?",
               "from_id": created_user_1_id, "to_id": created_user_2_id}

        async with async_client.websocket_connect("/chat/ws") as ws:
            await ws.send_bytes(orjson.dumps({
                "user_id": created_user_1_id,
            }))
            await ws.send_bytes(orjson.dumps({
                "action": WSAction.CREATE,
                "message": msg,
            }))
            resp = orjson.loads(await ws.receive_bytes())

        assert resp["status"] == WSStatus.OK
        assert resp["message"] == {
            "id": IsUUID(),
            "match_id": created_match_id,
            "from_id": created_user_1_id,
            "to_id": created_user_2_id,
            "text": "Пр, го встр?",
            "status": str(MessageStatus.SENT),
            "updated_at": IsStr(),
        }
        """Создание сообщений вторым пользователем."""

        msg = {"match_id": created_match_id, "text": "Го)))",
               "from_id": created_user_2_id, "to_id": created_user_1_id}

        async with async_client.websocket_connect("/chat/ws") as ws:
            await ws.send_bytes(orjson.dumps({
                "user_id": created_user_1_id,
            }))
            await ws.send_bytes(orjson.dumps({
                "action": WSAction.CREATE,
                "message": msg,
            }))
            resp = orjson.loads(await ws.receive_bytes())

        assert resp["status"] == WSStatus.OK
        assert resp["message"] == {
            "id": IsUUID(),
            "match_id": created_match_id,
            "from_id": created_user_2_id,
            "to_id": created_user_1_id,
            "text": "Го)))",
            "status": str(MessageStatus.SENT),
            "updated_at": IsStr(),
        }