from fastapi import APIRouter

from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserCreateInput, UserCreateOutput

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(fastapi_users.get_auth_router(auth_backend),)
router.include_router(fastapi_users.get_register_router(
    UserCreateInput, UserCreateOutput
))
