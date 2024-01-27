from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud, schemas
from src.auth.base_config import AuthHandler, current_user
from src.auth.crud import create_user
from src.auth.models import AuthUser
from src.auth.schemas import ResponseSchema, UserCreateInput, UserSchema
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
):
    """Регистрация нового пользователя c выдачей ему access и refresh token."""
    if not (user := await create_user(user_data, session)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid user data",
        )
    AuthHandler.create_access_token(response, user)
    AuthHandler.create_refresh_token(response, user)
    return UserSchema(**user.dict())


@auth_router.post(
    "/login",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def login(
    response: Response,
    user: Annotated[UserCreateInput, Depends(AuthHandler.validate_auth_user)],
) -> ResponseSchema:
    """Проверка и вход пользователя c выдачей ему access и refresh token."""
    AuthHandler.create_access_token(response, user)
    AuthHandler.create_refresh_token(response, user)
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail=user.email,
    )


@auth_router.get(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    response: Response,
    user: Annotated[UserSchema, Depends(AuthHandler.check_user_refresh_token)],
) -> dict:
    """Обновление access_token при наличии действующего refresh_token."""
    AuthHandler.create_access_token(response, user)
    AuthHandler.create_refresh_token(response, user)
    return {"status_code": status.HTTP_200_OK}


@auth_router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    response: Response,
    _: Annotated[UserSchema, Depends(current_user)],
) -> dict:
    """Выход пользователя c удалением файлов куки из браузера."""
    AuthHandler.delete_all_tokens(response)
    return {"status_code": status.HTTP_204_NO_CONTENT}


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
