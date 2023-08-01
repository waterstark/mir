import datetime
import uuid
from pathlib import Path
from httpx import AsyncClient
import pytest
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import ac
from src.auth.models import AuthUser
from src.database import Base
from src.questionnaire.models import UserQuestionnaire


@pytest.mark.asyncio()
async def test_uuid(session: AsyncSession):
    new_user = {
        "email": "mail@server.com",
        "created_at": datetime.datetime.utcnow(),
        "hashed_password": "pass",
        "is_active": False,
        "is_superuser": False,
        "is_verified": False,
        "is_delete": False,
    }

    # TODO: replace when crud appears
    stmt = insert(AuthUser).values(new_user).returning(AuthUser)
    user = (await session.execute(stmt)).one_or_none()

    assert user is not None
    assert isinstance(user[0].id, uuid.UUID)


@pytest.mark.asyncio()
async def test_table_names_and_columns():
    with Path("data/reserved_keywords.txt").open(encoding="utf-8") as f:
        reserved = set(f.readlines())

    for table in Base.metadata.tables:
        assert table.lower() not in reserved


# @pytest.mark.asyncio()
# async def test_create_questionnaire(ac: AsyncClient):
#     user_questionnaire = {
#         "firstname": "nikita",
#         "lastname": "pupkin",
#         "gender": "pass",
#         "photo": "False",
#         "country": "False",
#         "city": "False",
#         "about": "False",
#         "passion": "False",
#         "height": 150,
#         "goals": "False",
#         "body_type": "False",
#     }
#     resp = await ac.post(
#         "/quest/questionnaire",
#         json=user_questionnaire,
#     )
#     assert resp.status_code == 201
