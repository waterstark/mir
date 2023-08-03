import logging
from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.auth.models import AuthUser
from src.auth.utils import get_user_db
from src.database import Base

logging.basicConfig(filename="example.log", filemode="w", level=logging.DEBUG)
logger = logging.getLogger("mir_logger")


class UserManager(UUIDIDMixin, BaseUserManager[AuthUser, int]):
    async def on_after_register(self, user: AuthUser, request: Request | None = None):
        logger.info(f"User {user.id} has registered.")


async def get_user_manager(user_db: Annotated[Base, Depends(get_user_db)]):
    yield UserManager(user_db)
