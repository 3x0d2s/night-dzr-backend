from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.sql.db import Base, engine
from src.auth.auth import auth_backend, fastapi_users
from src.schemas.user import UserRead, UserCreate, UserUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="NightDozor_Backend",
    description="Backend сервиса для проведения игры Ночной Дозор.",
    version="dev-0.1.0",
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
