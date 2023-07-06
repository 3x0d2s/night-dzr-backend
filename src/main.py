from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database.db import engine
from src.auth.auth import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.teams.router import router as teams_router
from src.tasks.router import router as tasks_router
from src.games.router import router as games_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="NightDozor_Backend",
    description="Backend сервиса для проведения игры Ночной Дозор.",
    version="dev-0.2.0",
    lifespan=lifespan
)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    teams_router,
    tags=["teams"],
)
app.include_router(
    tasks_router,
    tags=["tasks"],
)
app.include_router(
    games_router,
    tags=["games"],
)
