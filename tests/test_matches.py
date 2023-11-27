import pytest
from async_asgi_testclient import TestClient
from dirty_equals import IsTrueLike, IsUUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.likes.crud import get_like_by_id
from src.likes.models import UserLike
from src.main import app
from src.matches.crud import get_match_by_id
from src.matches.models import Match
from src.questionnaire.models import UserQuestionnaire


class TestMatch:
    """Тесты эндпоинтов matches/ и matches/{match_id}"""

    matches_url = app.url_path_for("get_matches")

    async def test_access_not_authenticated_matches_list(
        self,
        user2: AuthUser,
        async_client: TestClient,
    ):
        """Проверка существования эндпоинта matches/ и наличия
        доступа к нему неавторизованного пользователя
        """

        response = await async_client.get(self.matches_url)

        assert (
            response.status_code != status.HTTP_404_NOT_FOUND
        ), f"Эндпоинт `{self.matches_url}` не найден."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            "Проверьте, что GET-запрос неавторизованного пользователя к "
            f"`{self.matches_url}` возвращает код 401"
        )

    async def test_matches_list(
        self,
        authorised_cookie: dict,
        async_client: TestClient,
        user: AuthUser,
        user2: AuthUser,
        match: Match,
        match2: Match,
        questionary: UserQuestionnaire,
    ):
        """Проверка корректности работы эндпоинта matches/ при
        GET-запросе авторизованного пользователя
        """
        response = await async_client.get(
            self.matches_url,
            cookies=authorised_cookie,
        )

        assert response.status_code == status.HTTP_200_OK, (
            "Проверьте, что GET-запрос неавторизованного пользователя к "
            f"`{self.matches_url}` возвращает код 200"
        )

        response_json = response.json()
        assert isinstance(response_json, list), (
            "Проверьте, что GET-запрос авторизованного "
            f"пользователя к `{self.matches_url}` возвращает "
            "список анкет пользователей, c которыми есть match"
        )

        assert len(response_json) == 1, (
            "Проверьте, что GET-запрос авторизованного пользователя "
            f"к `{self.matches_url}` не возвращает анкеты пользователей,"
            "c которыми нет совпадения"
        )

        assert response.json()[0] == {
            "firstname": questionary.firstname,
            "lastname": questionary.lastname,
            "gender": questionary.gender,
            "photo": questionary.photo,
            "country": questionary.country,
            "city": questionary.city,
            "about": questionary.about,
            "age": questionary.age,
            "hobbies": [
                {
                    "hobby_name": questionary.hobbies[0].hobby_name,
                },
                {
                    "hobby_name": questionary.hobbies[1].hobby_name,
                },
            ],
            "height": questionary.height,
            "goals": questionary.goals,
            "body_type": questionary.body_type,
            "user_id": IsUUID,
            "id": IsUUID,
            "is_match": IsTrueLike,
        }, (
            "Проверьте, что GET-запрос авторизованного пользователя "
            f"к `{self.matches_url}` возвращает анкету c корректными данными"
        )

    async def test_access_not_authenticated_match_delete(
        self,
        async_client: TestClient,
        user2: AuthUser,
        match: Match,
    ):
        """Проверка существования эндпоинта удаления match и
        доступа к нему неавторизованного пользователя
        """
        match_delete_url = app.url_path_for("match_delete", match_id=match.id)
        response = await async_client.delete(match_delete_url)

        assert (
            response.status_code != status.HTTP_404_NOT_FOUND
        ), f"Эндпоинт `{match_delete_url}` не найден."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            "Проверьте, что GET-запрос неавторизованного пользователя к "
            f"`{match_delete_url}` возвращает код 401"
        )

    async def test_valid_match_delete(
        self,
        async_client: TestClient,
        user: AuthUser,
        match: Match,
        authorised_cookie: dict,
        like1: UserLike,
        like2: UserLike,
        get_async_session: AsyncSession,
    ):
        """Проверка валидного DELETE-запроса к эндпоинту matches/{match_id}"""
        match_delete_url = app.url_path_for("match_delete", match_id=match.id)
        response = await async_client.delete(
            match_delete_url,
            cookies=authorised_cookie,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            "Проверьте, что валидный DELETE-запрос авторизованного "
            f"пользователя к `{match_delete_url}` возвращает "
            "код 204"
        )

        assert await get_match_by_id(get_async_session, match.id) is None, (
            "Проверьте, что валидный DELETE-запрос авторизованного "
            f"пользователя к `{match_delete_url}` удаляет объект Match"
        )

        assert await get_like_by_id(get_async_session, like1.id) is None, (
            "Проверьте, что валидный DELETE-запрос авторизованного "
            f"пользователя к `{match_delete_url}` удаляет также лайк удалившего"
            "match пользователя"
        )

        assert await get_like_by_id(get_async_session, like2.id), (
            "Проверьте, что валидный DELETE-запрос авторизованного "
            f"пользователя к `{match_delete_url}` не удаляет лайк "
            "другого пользователя"  # Хотя возможно и должен удалять, пока оставлю так.
        )

    # incorrect table state
    @pytest.mark.skip()
    async def test_invalid_match_delete(
        self,
        async_client: TestClient,
        user2: AuthUser,
        match1: Match,
        authorised_cookie: dict,
        like1: UserLike,
        get_async_session: AsyncSession,
    ):
        """Проверка невалидного DELETE-запроса к эндпоинту matches/{match_id}"""
        match_delete_url = app.url_path_for("match_delete", match_id=match1.id)
        response = await async_client.delete(
            match_delete_url,
            cookies=authorised_cookie,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            "Проверьте, что при попытке удалить не свой match "
            f"через DELETE-запрос к `{match_delete_url}`, "
            "возвращается код 403"
        )

        assert await get_match_by_id(get_async_session, match1.id), (
            "Проверьте, что DELETE-запрос некорректного "
            f"пользователя к `{match_delete_url}` не удаляет объект Match"
        )

        assert await get_like_by_id(get_async_session, like1.id), (
            "Проверьте, что DELETE-запрос некорректного "
            f"пользователя к `{match_delete_url}` не удаляет лайк пользователей"
        )
