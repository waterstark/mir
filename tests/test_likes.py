import pytest
from async_asgi_testclient import TestClient
from dirty_equals import IsUUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.likes.crud import get_retreive_like
from src.likes.models import UserLike
from src.likes.schemas import UserLikeRequest
from src.main import app
from src.matches.crud import get_retreive_match
from src.matches.schemas import MatchRequest
from src.questionnaire.models import UserQuestionnaire


class TestLike:
    """Тесты эндпоинта users/{user_id}/like"""

    async def test_access_not_authenticated_like_create(
        self,
        user: AuthUser,
        async_client: TestClient,
    ):
        """Проверка существования эндпоинта users/{user_id}/like и наличия
        доступа к нему неавторизованного пользователя
        """
        create_like_url = app.url_path_for("like_user_by_id", user_id=user.id)
        response = await async_client.post(create_like_url)

        assert (
            response.status_code != status.HTTP_404_NOT_FOUND
        ), f"Эндпоинт `{create_like_url}` не найден."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            "Проверьте, что POST-запрос неавторизованного пользователя к "
            f"`{create_like_url}` возвращает код 401"
        )

    async def test_valid_like_create(
        self,
        user: AuthUser,
        user2: AuthUser,
        questionary: UserQuestionnaire,
        authorised_cookie: dict,
        async_client: TestClient,
        get_async_session: AsyncSession,
    ):
        """Проверка валидного POST-запроса к эндпоинту users/{user_id}/like"""

        create_like_url = app.url_path_for("like_user_by_id", user_id=user2.id)
        response = await async_client.post(
            create_like_url,
            cookies=authorised_cookie,
        )

        assert response.status_code == status.HTTP_201_CREATED, (
            "Проверьте, что POST-запрос авторизованного пользователя к "
            f"`{create_like_url}` возвращает код 201"
        )

        assert await get_retreive_like(
            get_async_session,
            UserLikeRequest(user_id=user.id, liked_user_id=user2.id),
        ), (
            "Проверьте, что POST-запрос авторизованного пользователя к "
            f"`{create_like_url}` создаёт объект like в БД"
        )

        assert response.json() == {
            "id": IsUUID,
            "firstname": questionary.firstname,
            "lastname": questionary.lastname,
            "gender": questionary.gender,
            "photo": questionary.photo,
            "country": questionary.country,
            "city": questionary.city,
            "about": questionary.about,
            "height": questionary.height,
            "goals": questionary.goals,
            "body_type": questionary.body_type,
            "user_id": IsUUID,
            "is_match": False,
            "age": questionary.age,
            "hobbies": [
                {
                    "hobby_name": questionary.hobbies[0].hobby_name,
                },
                {
                    "hobby_name": questionary.hobbies[1].hobby_name,
                },
            ],
        }, (
            "Проверьте, что ответ на POST-запрос авторизованного пользователя к "
            f"`{create_like_url}` содержит анкету понравившегося пользователя "
        )

    # skip because match creation after like is not implemented
    @pytest.mark.skip()
    async def test_valid_match_create_with_like_create(
        self,
        user: AuthUser,
        user2: AuthUser,
        like2: UserLike,
        questionary: UserQuestionnaire,
        authorised_cookie: dict,
        async_client: TestClient,
        get_async_session: AsyncSession,
    ):
        """Проверка создания объекта Match в случае, когда при
        POST-запросе к эндпоинту users/{user_id}/like уже существует обратный лайк
        """
        create_like_url = app.url_path_for("like_user_by_id", user_id=user2.id)
        response = await async_client.post(
            create_like_url,
            cookies=authorised_cookie,
        )
        assert await get_retreive_match(
            get_async_session,
            MatchRequest(user1_id=user.id, user2_id=user2.id),
        ), (
            "Проверьте, что POST-запрос авторизованного пользователя к "
            f"`{create_like_url}` создаёт объект like в БД"
        )

        assert response.json().get("is_match"), (
            "Проверьте, что при в случае совпадения лайков при POST-запросе"
            f" авторизованного пользователя к `{create_like_url}` "
            "ответ содержит анкету c 'is_match':True"
        )
