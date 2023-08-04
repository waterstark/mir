from fastapi import APIRouter, Depends
from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.auth.base_config import auth_backend, fastapi_users_auth
from src.auth.schemas import UserCreateInput, UserCreateOutput

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(fastapi_users_auth.get_auth_router(auth_backend))
router.include_router(fastapi_users_auth.get_register_router(
    UserCreateOutput, UserCreateInput,
))


@router.get("/authenticated-route")
async def authenticated_route(
        user: AuthUser = Depends(current_user)
):
    return {"message": f"Hello {user.email}!"}
