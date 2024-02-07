import orjson
from async_asgi_testclient import TestClient
from sqlalchemy import delete, select, update
from dirty_equals import IsStr, IsUUID
from fastapi import status

from src.chat.schemas import MessageStatus, WSAction, WSStatus
from src.chat.utils import orjson_dumps


class TestAcceptance:
    """Тесты на поведение пользователя."""

    async def test_acceptance(self, async_client: TestClient):
        """1. Регистрация двух пользователей."""
        """2. Логины двух пользователей."""
        """3. Создание анкет двух пользователей."""
        """4. Взаимные лайки двух пользователей."""
        """5. Проверка матча."""

        """Регистрация двух пользователей."""

        user_1_data = {
            "email": "user1@mail.ru",
            "password": "password",
        }
        response = await async_client.post(
            "/api/v1/auth/register",
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
            "/api/v1/auth/register",
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

        """Логин пользователя 1."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json=user_1_data,
        )
        assert response.status_code == status.HTTP_200_OK

        created_user_1_jwt = async_client.cookie_jar["mir"].value

        """Логин пользователя 2."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json=user_2_data,
        )
        assert response.status_code == status.HTTP_200_OK

        created_user_2_jwt = async_client.cookie_jar["mir"].value

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
        }

        response = await async_client.post(
            "/api/v1/questionnaire",
            json=questionnaire_1_data,
            cookies={"mir": created_user_1_jwt},
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
        }
        response = await async_client.post(
            "/api/v1/questionnaire",
            json=questionnaire_2_data,
            cookies={"mir": created_user_2_jwt},
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

        """Проверка анкет первым пользователем."""

        response = await async_client.get(
            "/api/v1/questionnaire/list/0",
            cookies={"mir": created_user_1_jwt},
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

        response = await async_client.get(
            "/api/v1/questionnaire/list/0",
            cookies={"mir": created_user_1_jwt},
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

        response = await async_client.get(
            "/api/v1/questionnaire/list/0",
            cookies={"mir": created_user_1_jwt},
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

        response = await async_client.get(
            "/api/v1/questionnaire/list/0",
            cookies={"mir": created_user_1_jwt},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        response = await async_client.get(
            "/api/v1/questionnaire/list/0",
            cookies={"mir": created_user_1_jwt},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        """Первый пользователь лайкает второго."""

        like_1 = {
            "liked_user_id": created_user_2_id,
            "is_liked": True,
        }

        response = await async_client.post(
            "/api/v1/likes",
            json=like_1,
            cookies={"mir": created_user_1_jwt},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "created_at": IsStr,
            "id": IsUUID,
            "liked_user_id": created_user_2_id,
            "is_liked": True,
        }

        """Проверка анкет вторым пользователем."""

        response = await async_client.get(
            "/api/v1/questionnaire/list/0",
            cookies={"mir": created_user_2_jwt},
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

        like_2 = {
            "liked_user_id": created_user_1_id,
            "is_liked": True,
        }

        response = await async_client.post(
            "/api/v1/likes",
            json=like_2,
            cookies={"mir": created_user_2_jwt},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "created_at": IsStr,
            "id": IsUUID,
            "liked_user_id": created_user_1_id,
            "is_liked": True,
        }

        """Проверка матча вторым пользователем."""

        response = await async_client.get(
            "/api/v1/matches",
            cookies={"mir": created_user_2_jwt},
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
            "is_match": True,
        }]

        """Проверка анкет вторым пользователем после матча."""

        response = await async_client.get(
            "/api/v1/questionnaire/list/0",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []




    async def test_acceptance_with_chat(self, async_client: TestClient):
        """Тесты на чат между пользователями (пользователи взяты из предыдущего теста)."""

        """1. Логины двух пользователей."""
        """2. Получение различных id."""
        """3. Переписка (Работает только при подключении MongoDB)."""

        """Логин пользователя 1."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "user1@mail.ru",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        user1_cookie = {"mir": async_client.cookie_jar["mir"].value}

        """Получаем id матча."""

        response = await async_client.get(
            "/api/v1/matches",
        )
        created_match_id = response.json()[0]["id"]

        """Получаем id первого пользователя."""

        response = await async_client.get(
            "/api/v1/users/me",
        )
        created_user_1_id = response.json()["user_id"]

        """Логин пользователя 2."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "user2@mail.ru",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        user2_cookie = {"mir": async_client.cookie_jar["mir"].value}
        """Получаем id Второго пользователя."""

        response = await async_client.get(
            "/api/v1/users/me",
        )
        created_user_2_id = response.json()["user_id"]

        """Создание сообщений первым пользователем."""

        msg = {"match_id": created_match_id, "text": "Hi, lets meet up?",
               "from_id": created_user_1_id, "to_id": created_user_2_id}

        async with async_client.websocket_connect("/chat/ws", cookies=user1_cookie) as ws:
            await ws.send_text(orjson_dumps({
                "action": WSAction.CREATE,
                "message": msg,
            }))
            resp = orjson.loads(await ws.receive_text())

        assert resp["status"] == WSStatus.OK
        assert resp["message"] == {
            "id": IsUUID(),
            "match_id": created_match_id,
            "from_id": created_user_1_id,
            "to_id": created_user_2_id,
            "text": "Hi, lets meet up?",
            "status": str(MessageStatus.SENT),
            "created_at": IsStr(),
            "updated_at": IsStr(),
            "reply_to": None,
            "group_id": None,
            "media": None,
        }

        """Создание сообщений первым пользователем."""

        msg = {"match_id": created_match_id, "text": "Ok)))",
               "from_id": created_user_2_id, "to_id": created_user_1_id}

        async with async_client.websocket_connect("/chat/ws", cookies=user2_cookie) as ws:
            await ws.send_text(orjson_dumps({
                "action": WSAction.CREATE,
                "message": msg,
            }))
            resp = orjson.loads(await ws.receive_text())

        assert resp["status"] == WSStatus.OK
        assert resp["message"] == {
            "id": IsUUID(),
            "match_id": created_match_id,
            "from_id": created_user_2_id,
            "to_id": created_user_1_id,
            "text": "Ok)))",
            "status": str(MessageStatus.SENT),
            "created_at": IsStr(),
            "updated_at": IsStr(),
            "reply_to": None,
            "group_id": None,
            "media": None,
        }
