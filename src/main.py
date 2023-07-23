from fastapi import FastAPI

from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserCreate, UserRead
from src.posts.routers import router as router_post

app = FastAPI(title="social networking application", docs_url="/")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_post)
