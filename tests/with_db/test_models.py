import datetime
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.database import Base


async def test_uuid(get_async_session: AsyncSession):
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
    async with get_async_session as db:
        created_user = AuthUser(**new_user)
        db.add(created_user)
        await db.commit()
    assert isinstance(created_user.id, uuid.UUID)


async def test_table_names_and_columns():
    with Path("data/reserved_keywords.txt").open(encoding="utf-8") as f:
        reserved = set(f.readlines())

    for table in Base.metadata.tables:
        assert table.lower() not in reserved
