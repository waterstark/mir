import datetime
import uuid
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.database import Base


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


@pytest.mark.asyncio()
async def test_get_list_questionnaire(ac: AsyncClient):
    resp = await ac.get("/quest/all-quest")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio()
async def test_create_questionnaire(ac: AsyncClient):
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
    resp = await ac.post(
        "/quest/add-quest",
        json=user_questionnaire,
    )
    assert resp.status_code == 201


@pytest.mark.asyncio()
async def test_update_quest(ac: AsyncClient):
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
    resp = await ac.patch("/quest/update/{d5c5f699-0f9e-4499-af2b-f0723349e9f9}",
                          json=update_user_quest)
    assert resp.status_code == 200


@pytest.mark.asyncio()
async def test_delete_quest(ac: AsyncClient):
    resp = await ac.delete("/quest/{d5c5f699-0f9e-4499-af2b-f0723349e9f9}")
    assert resp.status_code == 204
