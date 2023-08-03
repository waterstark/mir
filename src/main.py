from fastapi import APIRouter, FastAPI, Depends
from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.auth.routers import router as auth_router
from src.questionnaire.routers import router as questionnaire_router

app = FastAPI(
    title="social networking application",
    docs_url="/",
)

main_router = APIRouter(prefix="/api/v1")
main_router.include_router(auth_router)

app.include_router(main_router)
app.include_router(questionnaire_router)


@app.get("/authenticated-route")
async def authenticated_route(
        user: AuthUser = Depends(current_user)
):
    return {"message": f"Hello {user.email}!"}
