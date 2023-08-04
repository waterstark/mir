from fastapi import APIRouter, FastAPI

from src.auth.routers import router as auth_router
from src.likes.router import likes_router
from src.questionnaire.routers import router as questionnaire_router

app = FastAPI(
    title="social networking application",
    docs_url="/",
)

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(auth_router)
main_router.include_router(likes_router)
app.include_router(questionnaire_router)

app.include_router(main_router)
