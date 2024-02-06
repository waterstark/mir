from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import base_config as auth_handler
from src.auth import crud, schemas
from src.auth.base_config import current_user
from src.auth.crud import create_user
from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput, UserSchema
from src.database import get_async_session

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@auth_router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    response: Response,
    user_data: UserCreateInput,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserSchema:
    """Регистрация нового пользователя c выдачей ему access и refresh token."""
    user = await create_user(user_data, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid user data",
        )
    token_access = auth_handler.create_access_token(user)
    token_refresh = auth_handler.create_refresh_token(user)
    response.set_cookie(token_access["type_token"], token_access["token"], httponly=True, secure=True)
    response.set_cookie(token_refresh["type_token"], token_refresh["token"], httponly=True, secure=True)
    return user


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    response: Response,
    user: Annotated[UserCreateInput, Depends(auth_handler.validate_auth_user)],
) -> dict:
    """Проверка и вход пользователя c выдачей ему access и refresh token."""
    token_access = auth_handler.create_access_token(user)
    token_refresh = auth_handler.create_refresh_token(user)
    response.set_cookie(token_access["type_token"], token_access["token"], httponly=True, secure=True)
    response.set_cookie(token_refresh["type_token"], token_refresh["token"], httponly=True, secure=True)
    return {"status_code": status.HTTP_200_OK}


@auth_router.get(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    response: Response,
    user: Annotated[AuthUser, Depends(auth_handler.check_user_refresh_token)],
) -> dict:
    """Обновление access_token при наличии действующего refresh_token."""
    token_access = auth_handler.create_access_token(user)
    token_refresh = auth_handler.create_refresh_token(user)
    response.set_cookie(token_access["type_token"], token_access["token"], httponly=True, secure=True)
    response.set_cookie(token_refresh["type_token"], token_refresh["token"], httponly=True, secure=True)
    return {"status_code": status.HTTP_200_OK}


@auth_router.get(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    response: Response,
) -> None:
    """Выход пользователя c удалением файлов куки из браузера."""
    return auth_handler.delete_all_tokens(response)


user_router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@user_router.get(
    "/me",
    response_model=schemas.UserProfile,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    user: Annotated[AuthUser, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> schemas.UserProfile:
    return await crud.get_user_profile(user=user, session=session)


@user_router.patch(
    "/me",
    response_model=schemas.UserProfile,
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    data: schemas.UserProfileUpdate,
    user: Annotated[AuthUser, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> schemas.UserProfile:
    """Update user profile."""
    return await crud.update_user_profile(
        data=data,
        user=user,
        session=session,
    )
