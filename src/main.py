from contextlib import asynccontextmanager
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from src.admin import admin
from src.auth.routers import auth_router, user_router
from src.chat.routers import ws_router
from src.likes.routers import likes_router
from src.matches.routers import router as matches_router
from src.questionnaire.crud import reset_quest_lists_per_day, reset_age_validation
from src.questionnaire.routers import router as questionnaire_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await reset_age_validation()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        reset_quest_lists_per_day,
        "interval",
        seconds=5,
    )
    scheduler.add_job(
        reset_age_validation,
        "interval",
        seconds=30,
    )
    scheduler.start()
    yield

app = FastAPI(
    title="social networking application",
    docs_url="/",
    lifespan=lifespan,
    routes=[
        Mount(
            "/static",
            app=StaticFiles(directory="static"),
            name="static",
        ),
    ],
)

# Настройка CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin.mount_to(app)

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(likes_router)
main_router.include_router(questionnaire_router)
main_router.include_router(matches_router)

# TODO: change to wss for production
app.include_router(ws_router)

app.include_router(main_router)
