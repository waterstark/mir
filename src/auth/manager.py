import logging
import uuid
from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.auth import crud
from src.auth.models import AuthUser
from src.auth.utils import get_user_db
from src.config import settings
from src.database import Base, async_session_maker

logging.basicConfig(filename="example.log", filemode="w", level=logging.DEBUG)
logger = logging.getLogger("mir_logger")


class UserManager(UUIDIDMixin, BaseUserManager[AuthUser, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(
        self,
        user: AuthUser,
        request: Request | None = None,
    ):
        async with async_session_maker() as session:
            await crud.create_user_profile(user=user, session=session)
        logger.info(f"User {user.id} has registered.")


async def get_user_manager(user_db: Annotated[Base, Depends(get_user_db)]):
    yield UserManager(user_db)
