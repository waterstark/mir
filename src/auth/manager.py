
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from src.auth.models import User
from src.auth.utils import get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
