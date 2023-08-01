from fastapi import APIRouter, FastAPI

from src.auth.routers import router as auth_router


app = FastAPI(
    title="social networking application",
    docs_url="/",
)

main_router = APIRouter(prefix='/api/v1')
main_router.include_router(auth_router)

app.include_router(main_router)
