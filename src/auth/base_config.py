from fastapi_users_auth import FastAPIUsers
from fastapi_users_auth.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

from src.auth.manager import get_user_manager
from src.auth.models import AuthUser
from src.config import SECRET_AUTH

cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_AUTH, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users_auth = FastAPIUsers[AuthUser, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users_auth.current_user()
