from fastapi import APIRouter, FastAPI
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from src.admin import admin
from src.auth.routers import router as auth_router
from src.questionnaire.routers import router as questionnaire_router

app = FastAPI(
    title="social networking application",
    docs_url="/",
    routes=[
        Mount(
            '/static', app=StaticFiles(directory='static'), name='static'
        ),
    ]
)

admin.mount_to(app)

main_router = APIRouter(prefix="/api/v1")
main_router.include_router(auth_router)

app.include_router(main_router)
app.include_router(questionnaire_router)
