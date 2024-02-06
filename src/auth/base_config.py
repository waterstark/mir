from typing import Annotated

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import APIKeyCookie
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.crud import get_user
from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput
from src.config import settings
from src.database import get_async_session

cookies_access_scheme = APIKeyCookie(name=settings.COOKIE_ACCESS_TOKEN_KEY)
cookies_refresh_scheme = APIKeyCookie(name=settings.COOKIE_REFRESH_TOKEN_KEY)


async def validate_auth_user(
    user_login: UserCreateInput,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthUser:
    """Идентификация данных пользователя."""
    unauthenticated_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="invalid username or password",
    )
    user = await get_user(user_login.email, session)
    _verify_user(
        user=user,
        user_password=user_login.password,
        custom_exception=unauthenticated_exception,
    )
    return user


def _verify_user(
    user: AuthUser,
    user_password: str | bytes,
    custom_exception: HTTPException,
) -> None:
    if not user:
        raise custom_exception
    if not auth_utils.validate_password(
        password=user_password,
        hashed_password=user.hashed_password,
    ):
        raise custom_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        ) from None


async def get_auth_user(
    access_token: Annotated[str, Depends(cookies_access_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthUser:
    """
    Получение данных аутентифицированного пользователя.
    Функция проверяет подлинность пользователя и дает
    доступ к использованию закрытых эндпоинтов.
    """
    try:
        payload = auth_utils.decode_jwt(
            token=access_token,
        )
        user = await _check_token_data(payload, session)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error",
        ) from None
    return user


async def check_user_refresh_token(
    refresh_token: Annotated[str, Depends(cookies_refresh_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthUser:
    """Проверка refresh token на подлинность."""
    try:
        payload = auth_utils.decode_jwt(
            token=refresh_token,
        )
        user = await _check_token_data(payload, session)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="could not refresh access token",
        ) from None
    return user


async def _check_token_data(
    payload: dict,
    session: AsyncSession,
) -> AuthUser:
    """Функция проверки данных токена."""
    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not refresh access token",
        )
    email: str = payload.get("email")
    user = await get_user(email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="the user no longer exists",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )
    return user


def _create_token(
    type_token: str,
    expires_time: int,
    data: AuthUser,
) -> dict:
    """Функция создания токена по заданным параметрам."""
    jwt_payload = {
        "sub": str(data.id),
        "email": data.email,
        "type": type_token,
    }
    token = auth_utils.encode_jwt(jwt_payload, expire_minutes=expires_time)
    return {"type_token": type_token, "token": token}


def create_access_token(
    user_data: Annotated[AuthUser, Depends(validate_auth_user)],
) -> dict:
    """Создание access_token."""
    return _create_token(
        type_token=settings.COOKIE_ACCESS_TOKEN_KEY,
        expires_time=settings.ACCESS_TOKEN_EXPIRES_IN,
        data=user_data,
    )


def create_refresh_token(
    user_data: Annotated[AuthUser, Depends(validate_auth_user)],
) -> dict:
    """Создание refresh_token."""
    return _create_token(
        type_token=settings.COOKIE_REFRESH_TOKEN_KEY,
        expires_time=settings.REFRESH_TOKEN_EXPIRES_IN,
        data=user_data,
    )


def delete_all_tokens(
    response: Response,
) -> None:
    """Удаление всех токенов из браузера пользователя."""
    response.delete_cookie(settings.COOKIE_ACCESS_TOKEN_KEY, httponly=True, secure=True)
    response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY, httponly=True, secure=True)


current_user = get_auth_user
