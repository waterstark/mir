import datetime
import uuid

import pytest
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.auth.models import AuthUser


@pytest.mark.asyncio()
async def test_uuid(session: Session):
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
